import sys
import json
import time
import cp

# Import the function to get dish status from starlink_grpc.py
import starlink_grpc

def consolidate_status(raw_status):
    """
    Create a consolidated status string that fits within 255 characters.
    Formats the status to match the UI display format.
    """
    # Check if it's a gRPC object
    if not hasattr(raw_status, 'DESCRIPTOR'):
        # If it's not a gRPC object, return a basic error status
        return "Connected: 🔴 gRPC Error: (not a gRPC object)"
    
    # Determine state from the raw gRPC object (same logic as starlink_grpc.py)
    try:
        if hasattr(raw_status, 'outage') and raw_status.HasField("outage"):
            if hasattr(raw_status.outage, 'cause'):
                if raw_status.outage.cause == 1:  # NO_SCHEDULE
                    state = "SEARCHING"
                else:
                    state = f"OUTAGE_{raw_status.outage.cause}"
            else:
                state = "OUTAGE"
        else:
            state = "CONNECTED"
    except (AttributeError, ValueError):
        state = "UNKNOWN"
    
    # Extract key metrics
    downlink_bps = getattr(raw_status, "downlink_throughput_bps", 0)
    uplink_bps = getattr(raw_status, "uplink_throughput_bps", 0)
    latency_ms = getattr(raw_status, "pop_ping_latency_ms", 0)
    ping_drop_rate = getattr(raw_status, "pop_ping_drop_rate", 0)
    fraction_obstructed = getattr(getattr(raw_status, "obstruction_stats", None), "fraction_obstructed", 0)
    
    # Convert bps to Mbps
    downlink_mbps = downlink_bps / 1000000
    uplink_mbps = uplink_bps / 1000000
    
    # Determine connection status
    if state == "CONNECTED":
        connection_status = "Connected: 🟢"
    else:
        connection_status = f"Connected: 🔴"
    
    # Determine obstruction status
    if fraction_obstructed == 0:
        obstruction_status = "Unobstructed"
    else:
        obstruction_status = f"Obstructed ({fraction_obstructed:.1%})"
    
    # Format the status string
    status_string = f"{connection_status} Down: {downlink_mbps:.2f}Mbps | Up: {uplink_mbps:.2f}Mbps | Latency: {latency_ms:.0f}ms | Loss: {ping_drop_rate:.1%} | {obstruction_status}"
    
    # Truncate to 255 characters if needed
    if len(status_string) > 255:
        status_string = status_string[:252] + "..."
    
    return status_string

def grpc_to_dict(grpc_obj):
    """
    Convert a gRPC message object to a JSON-serializable dictionary.
    """
    if grpc_obj is None:
        return None
    
    # Check if it's actually a gRPC message object
    if not hasattr(grpc_obj, 'DESCRIPTOR'):
        # If it's not a gRPC object, return it as-is (could be a string or other type)
        return grpc_obj
    
    result = {}
    for field in grpc_obj.DESCRIPTOR.fields:
        value = getattr(grpc_obj, field.name)
        
        if field.type == field.TYPE_MESSAGE:
            if field.label == field.LABEL_REPEATED:
                # Handle repeated message fields
                result[field.name] = [grpc_to_dict(item) for item in value]
            else:
                # Handle single message fields
                result[field.name] = grpc_to_dict(value)
        elif field.type == field.TYPE_ENUM:
            # Handle enum fields
            if field.label == field.LABEL_REPEATED:
                result[field.name] = [item.name if hasattr(item, 'name') else str(item) for item in value]
            else:
                result[field.name] = value.name if hasattr(value, 'name') else str(value)
        else:
            # Handle primitive fields
            if field.label == field.LABEL_REPEATED:
                result[field.name] = list(value)
            else:
                result[field.name] = value
    
    return result

def pretty_status(status):
    """
    Convert the status dictionary to a single-line JSON string that's readable.
    """
    return json.dumps(status, separators=(',', ': '), sort_keys=True)

def main():
    # Run continuously with 5-minute intervals
    while True:
        try:
            # Get the raw dish status using starlink_grpc
            raw_status = starlink_grpc.get_status()
            
            # Convert the raw gRPC response to a JSON-serializable dictionary
            combined_status = grpc_to_dict(raw_status)
            
            # Add timestamp to the combined status
            combined_status['updated_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            
            # Put status to status/starlink
            try:
                cp.put('status/starlink', combined_status)
            except Exception as status_error:
                # If we can't update the status/starlink, at least log it
                print(f"Failed to update status/starlink: {status_error}")
                # Create a minimal error status for status/starlink
                error_status = {
                    "error": "gRPC timeout or connection error",
                    "state": "UNREACHABLE",
                    "updated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                }
                cp.put('status/starlink', error_status)

            # Check for active alerts and send cp.alert() for each one
            if hasattr(raw_status, 'alerts') and hasattr(raw_status.alerts, 'DESCRIPTOR'):
                for field in raw_status.alerts.DESCRIPTOR.fields:
                    alert_name = field.name
                    alert_value = getattr(raw_status.alerts, alert_name, False)
                    if alert_value:
                        cp.alert(f'Starlink Alert: {alert_name}')
                        print(f'Starlink Alert: {alert_name}')

            # Create consolidated status for asset_id (max 255 chars)
            consolidated = consolidate_status(raw_status)
            result = cp.put('config/system/asset_id', consolidated)
            cp.log(result)
            print(result)
            
        except Exception as e:
            # Handle errors gracefully
            error_msg = str(e)
            
            # Check for specific gRPC timeout errors
            if "DEADLINE_EXCEEDED" in error_msg or "Deadline Exceeded" in error_msg:
                error_status = "Connected: 🔴 Dish Unreachable (Timeout)"
            elif "grpc" in error_msg.lower():
                error_status = "Connected: 🔴 Dish Unreachable (gRPC Error)"
            else:
                error_status = f"Connected: 🔴 Error: {error_msg[:50]}"
            
            # Ensure error message fits within 255 characters
            if len(error_status) > 255:
                error_status = error_status[:252] + "..."
            
            cp.put('config/system/asset_id', error_status)
            print(f"Error occurred at {time.strftime('%Y-%m-%d %H:%M:%S')}: {e}")
        
        # Sleep for 5 minutes (300 seconds) before next update
        time.sleep(300)

if __name__ == "__main__":
    main()

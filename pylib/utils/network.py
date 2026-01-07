import socket
import threading

def resolve_host(host, timeout=1.0):
    """
    Resolve hostname to IP with a timeout.
    
    Args:
        host (str): The hostname to resolve.
        timeout (float): The timeout in seconds.
        
    Returns:
        str: The resolved IP address.
        
    Raises:
        socket.error: If resolution fails or times out.
    """
    try:
        # If it's already an IP, this returns it immediately
        socket.inet_aton(host)
        return host
    except socket.error:
        pass

    result = [None]
    error = [None]

    def target():
        try:
            result[0] = socket.gethostbyname(host)
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # Timeout occurred
        raise socket.error(f"Timeout resolving host '{host}'")
    
    if error[0]:
        raise socket.error(f"Could not resolve host '{host}': {error[0]}")
        
    return result[0]
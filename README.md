# multiple_api_request
Aim of this project is to provide possibility to perform multiple queries to servers APIs, more often than it is allowed to be done from the the single IP address.
IP adresses switching automaticaly (like round-robin algo).
So if, for example, server limits requests no more then in 30 seconds, we get 2 proxies - and now are able to perform reauests each 10 seconds - we have 3 distinct IP addresses.

# JWT KEY Management for Local Development

**Description**


The JWT_KEY and JWT_CERT_TEST environment variables references values not permitted to be stored in any repo or documentation. Due to the need of these values for Login.gov functionality 
 
Some backg
 


	
Private and public keys were generated so that as part of login.govs dashboard configuration we set the public key there.  The private key(JWT_KEY) is used by the Django app to encode the client assertion being sent to login.gov as part of the authentication process. 
	If you have access to the cloud.gov dashboard you'll find it under the env var JWT_KEY under the tdrs-backend deployment  as we don't currently have a KMS setup to manage passwords , keys, etc. 
	
	Or by using the Cloud Foundry CLI command after authenticating and setting the target/org : 
	
	`cf env tdp-backend`
	 
	If you don't have access to this I can share the key with you via google meet or any other secured means of communication you'd prefer 
	 
	The JWT_CERT_TEST value is a base64 encoded version of the public key used for unit tests
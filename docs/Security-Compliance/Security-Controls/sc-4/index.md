# System and Communications Protection
## SC-04 - Information in Shared Resources

The information system prevents unauthorized and unintended information transfer via shared system resources.

### TDP Implementation

**Data Files**
- Data files are uploaded to TDP by `Data Prepper` and `OFA Admin` users.
- TDP prevents `Data Prepper` users from uploading or downloading Data 
Files for any STT not associated with that user's profile
  - Frontend
      - Does not give the `Data Prepper` user the choice for which STT to upload or download files, but gives access to those files based on the STT indicated in the user's profile.  
      - Does not provide a way for the `Data Prepper` user to alter the STT they are requesting to upload or download Data Files for.
      - Users who do not have either the `Data Prepper` or `OFA Admin` role do not have access to Data File upload or download screens at all, so do not have access to a way to upload or download any files
  - Backend
      - Prevents `Data Prepper` users from uploading or downloading data files not associated with that user's STT by responding with an `Unauthorized` error if a request comes in for a data file with an STT that is not indicated in the user's profile. 
      - Prevents users without the `Data Prepper` or `OFA Admin` roles from uploading or downloading any Data Files by responding with an `Unauthorized` error when a user attempts to upload or download a file.
      
 **User Information**
 
 System user profile information is only accessible via the Django Admin interface. Access to this
 interface is restricted to `System Admin` users. All other users will receive an error if they attempt
 to access it.

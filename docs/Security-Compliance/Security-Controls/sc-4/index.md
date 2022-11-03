# System and Communications Protection
## SC-04 - Information in Shared Resources

The information system prevents unauthorized and unintended information transfer via shared system resources.

### TDP Implementation

**Data Files**
- Data files are uploaded to TDP by users with `Data Analyst` and `OFA Admin` roles.
- TDP prevents `Data Analyst` users from uploading or downloading data 
files for any state, tribal, or territory (STT) not associated with that user's profile
  - Frontend
      - Does not give the `Data Analyst` user the choice for which STT to upload or download files, but gives access to those files based on the STT indicated in the user's profile.  
      - Does not provide a way for the `Data Analyst` user to alter the STT they are requesting to upload or download Data Files for.
      - Users who do not have either the `Data Analyst` or `OFA Admin` role do not have access to data file upload or download screens at all, so do not have access to a way to upload or download any files
  - Backend
      - Prevents `Data Analyst` users from uploading or downloading data files not associated with that user's STT by responding with an `unauthorized` error if a request comes in for a data file with an STT that is not indicated in the user's profile. 
      - Prevents users without the `Data Analyst` or `OFA Admin` roles from uploading or downloading any data files by responding with an `unauthorized` error when a user attempts to upload or download a file.
      
 **User Information**
 
 System user profile information is only accessible via the Django Admin interface. Access to this
 interface is restricted to `OFA System Admin` users. All other users will receive an error if they attempt
 to access it.

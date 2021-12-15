# Pyha documentation

## In general

Pyha is a system for making, managing and monitoring material requests.

Pyha was been implemented for four groups of users:
- administrators
- authorities
- material owners
- lay people.

By logging in to the system, lay people can create new data requests for the system.
They can also download the files of the approved material requests and monitor the processing of
their material requests. Authorities are required to log in, after which they can go through the
material requesters, manage their status, and send questions to the material requesters.

A typical workflow involves a layman creating a data request with the system of their choice,
for the purpose, and with their contact information (accepting the privacy policy).
The authorities, and possibly the owners of the material, will be notified at sufficiently
short intervals (by e-mail) of requests for material which require them to take action.
Once all the parties controlling the request (authorities and owners of the file) have
taken a decision (accept / reject) on the request, the request is sent to the author
of the request. Notification (by e-mail).

In the case of approval, the notification contains a link through which the layman can
(after logging in) download the material corresponding to the material request.

The system provides an alternative function (environment variable) so that new requests
can only be handled by data controllers. In this case, the data controllers are also
responsible for managing the sensitive content of their own material in the material requests.

## System components

### Request Selection View (/ index)

The request selection view lists all the material requests made by the layman, as well as their
general information and status. For material owners, all material requests that contain the material
owner's materials are listed. All requests for material containing sensitive findings are listed
for the authorities.

### Requestview (/ requestview / id)

The status view of the request shows the layman all the information related to the request and
its status. In addition to the above, the owner of the material may make a decision to approve his
or her own material to the applicant. The authority may decide to label/make sensitive observations.

### Fill in the request form (/ requestform / id)

In the view, the layman fills the material request with the restrictions he / she has chosen,
for the purpose and with the contact information of the system (accepting the data protection
conditions).

### Checking out (/ logout)

Makes what is mentioned in the subheading.

### Interface (/ api /)

Provides an interface to other applications. ([Api Documentation] (Api.md))

### Interface to ajax queries (/ ajax /)

Provides an interface for ajax queries.

### Settings

Provides administrators with settings for customizing the software's automatic functionality.

## Architecture

### Database

Database information can be found here: [Database] (Database.md)

### Translations

Translation information can be found here: [Translation] (Translation.md)

### IDs

The tags to be hidden are defined in the environment variables.

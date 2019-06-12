#current role in session
USER = 'user'
ADMIN = 'admin'
HANDLER_ANY = 'handler'

#role categories
CAT_ADMIN = 'MA.admin'
CAT_HANDLER_SENS = 'MA.sensitiveInformationApprovalRequestHandler'
CAT_HANDLER_COLL = 'MA.downloadRequestHandler'
CAT_HANDLER_BOTH = CAT_HANDLER_SENS + ' and ' + CAT_HANDLER_COLL

ROLES_SHOWN_ROLE_IN_HEADER = {CAT_ADMIN,CAT_HANDLER_SENS,CAT_HANDLER_COLL}
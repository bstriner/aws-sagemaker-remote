

def get_account(session):
    return session.client('sts').get_caller_identity().get('Account')

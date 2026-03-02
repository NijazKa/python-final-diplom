# функция преобразования логина гитхаба в email, в случае если гитхаб не отдает почту

def ensure_email(strategy, details, backend, user=None, *args, **kwargs):
    if backend.name == 'github':
        email = details.get('email')

        if not email:
            username = details.get('username')
            email = f"{username}@github.local"
            details['email'] = email

    return {'details': details}
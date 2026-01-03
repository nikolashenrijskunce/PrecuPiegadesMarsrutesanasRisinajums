class User:
    def __init__(self, id, email, address, phone, password):
        self.id = id
        self.email = email
        self.address = address
        self.phone = phone
        self.password = password

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False
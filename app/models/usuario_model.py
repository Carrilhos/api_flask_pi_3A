class Usuario:
    def __init__(self, id_usuario, nome, sobrenome, email, senha, tipo_usuario='cliente'):
        self.id_usuario = id_usuario
        self.nome = nome
        self.sobrenome = sobrenome
        self.email = email
        self.senha = senha
        self.tipo_usuario = tipo_usuario

    def to_dict(self):
        return {
            "id": self.id_usuario,
            "nome_completo": f"{self.nome} {self.sobrenome}",
            "email": self.email,
            "tipo": self.tipo_usuario
        }
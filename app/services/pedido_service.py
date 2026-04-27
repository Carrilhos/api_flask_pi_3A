from app.repositories.endereco_repository import find_endereco_by_id
from app.repositories.anuncio_repository import find_anuncio_by_id
from app.repositories.pedido_repository import criar_pedido
from app.repositories.pedido_repository import cancelar_pedido
from app.repositories.pedido_repository import find_pedido_by_id

def criar_pedido_service(current_user_id, id_endereco, itens_front):
    """Processa os itens solicitados, valida o estoque, calcula o valor total, captura o snapshot do endereço e cria o pedido."""
    # Valida o endereço
    endereco = find_endereco_by_id(id_endereco)
    if not endereco or endereco["id_usuario"] != current_user_id:
        raise ValueError("Endereço inválido ou não pertence ao usuário logado.")

    # Processa os itens, calcula o total e valida estoque
    valor_total = 0.0
    itens_processados = []

    for item in itens_front:
        id_anuncio = item.get("id_anuncio")
        quantidade = int(item.get("quantidade", 0))

        if quantidade <= 0:
            raise ValueError(f"Quantidade inválida para o anúncio {id_anuncio}.")

        anuncio = find_anuncio_by_id(id_anuncio)
        if not anuncio:
            raise ValueError(f"Anúncio ID {id_anuncio} não encontrado.")

        if anuncio["estoque"] < quantidade:
            raise ValueError(f"Estoque insuficiente para o produto: {anuncio['titulo']}.")

        preco_unitario = float(anuncio["preco"])
        valor_total += preco_unitario * quantidade

        itens_processados.append({
            "id_anuncio": id_anuncio,
            "quantidade": quantidade,
            "preco": preco_unitario
        })

    # Monta o dicionário de Snapshots usando os dados reais do banco
    snaps = {
        "logradouro_snap": endereco["logradouro"],
        "numero_snap": endereco["numero"],
        "bairro_snap": endereco["bairro"],
        "cidade_snap": endereco["cidade"],
        "estado_snap": endereco["estado"],
        "cep_snap": endereco["cep"]
    }

    # Envia tudo para o repositório salvar usando uma transação segura
    return criar_pedido(current_user_id, valor_total, snaps, itens_processados)

def cancelar_pedido_service(current_user_id, id_pedido):
    """Cancela um pedido existente (se estiver pendente ou aprovado), validando a posse e realizando o estorno do estoque."""
    # Busca o pedido para garantir que existe
    pedido = find_pedido_by_id(id_pedido)

    # Verifica se o pedido pertence ao usuário 
    if not pedido or pedido["id_cliente"] != current_user_id:
        raise PermissionError("Pedido não encontrado ou acesso negado.")

    if pedido["status"] == "cancelado":
        raise ValueError("Este pedido já está cancelado.")

    # Só cancela de forma simples se estiver pendente ou aprovado
    if pedido["status"] not in ["pendente", "aprovado"]:
        raise ValueError(f"Não é possível cancelar um pedido que já está com status '{pedido['status']}'.")

    # Chama o repositório para estornar o estoque e mudar o status
    cancelar_pedido(id_pedido)
    
    return True
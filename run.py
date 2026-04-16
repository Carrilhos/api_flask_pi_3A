#Pai nosso que estais nos Céus,
#santificado seja o vosso Nome,
#venha a nós o vosso Reino,
#seja feita a vossa vontade assim na terra como no Céu.
#O pão nosso de cada dia nos dai hoje,
#perdoai-nos as nossas ofensas
#assim como nós perdoamos a quem nos tem ofendido,
#e não nos deixeis cair em tentação,
#mas livrai-nos do Mal.
#Amém.

#Garantia que vai funcionar

from app import create_app

app = create_app()
print("RUN.PY EXECUTADO")
if __name__ == "__main__":
    app.run(debug=True)
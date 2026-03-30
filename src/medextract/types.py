from typing import TypedDict


class ProductInfo(TypedDict):
    nome: str
    qt_lote: int
    lote: str
    dt_valid: str


class SurgeryInfo(TypedDict):
    descricao: str


class AccountInfos(TypedDict):
    internacao: str
    prontuario: str


class Account(TypedDict):
    paciente: str
    data_de_uso: str
    convenio: str
    medico: str
    cirurgias: SurgeryInfo
    produtos: list[ProductInfo]
    infos: AccountInfos


class StaCruzProduct(TypedDict):
    paciente: str
    data: str
    material: str
    qtd: str

"""Contratos de entrada e validação dos dados recebidos pelo estúdio."""

from typing import Literal

from pydantic import BaseModel, Field


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    style: str = Field(
        default="HQ humorística brasileira, traço expressivo, cores vibrantes.", max_length=800
    )


class TextModeIn(BaseModel):
    text_mode: Literal["ai", "editor"]


class ComicIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    context: str = Field(default="", max_length=6000)
    style: str | None = Field(default=None, max_length=800)  # None: novo = estilo do projeto; edição = mantém


class FrameIn(BaseModel):
    description: str = Field(max_length=6000)


class AssetIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    aliases: str = Field(default="", max_length=600)
    description: str = Field(default="", max_length=2000)
    personality: str = Field(default="", max_length=2000)
    traits: str = Field(default="", max_length=1000)
    avoid: str = Field(default="", max_length=1000)


class CastItemIn(BaseModel):
    asset_id: str
    included: bool = True
    role: str = Field(default="", max_length=300)


class CastIn(BaseModel):
    items: list[CastItemIn] = Field(default_factory=list, max_length=100)


class FrameCreateIn(BaseModel):
    kind: Literal["panel", "cover", "credits"] = "panel"


class KindIn(BaseModel):
    kind: Literal["panel", "cover"]


class FormatIn(BaseModel):
    format: Literal["landscape", "portrait", "square"]


class CreditLineIn(BaseModel):
    name: str = Field(default="", max_length=120)
    role: str = Field(default="", max_length=300)


class CreditsIn(BaseModel):
    heading: str = Field(default="Elenco", max_length=120)
    lines: list[CreditLineIn] = Field(default_factory=list, max_length=60)
    footer: str = Field(default="", max_length=1000)


class TailIn(BaseModel):
    x: float = Field(ge=-20, le=120)
    y: float = Field(ge=-20, le=120)


class BalloonIn(BaseModel):
    """Posições em % da imagem, para o balão acompanhar qualquer tamanho de tela."""

    id: str = Field(min_length=1, max_length=40)
    type: Literal["speech", "thought", "shout", "caption"] = "speech"
    text: str = Field(default="", max_length=600)
    speaker: str = Field(default="", max_length=40)
    x: float = Field(default=5, ge=-10, le=100)
    y: float = Field(default=5, ge=-10, le=100)
    w: float = Field(default=30, ge=8, le=100)
    size: float = Field(default=1, ge=0.5, le=2.5)
    tail: TailIn | None = None


class BalloonsIn(BaseModel):
    balloons: list[BalloonIn] = Field(default_factory=list, max_length=20)


class CostumesIn(BaseModel):
    costumes: dict[str, str] = Field(default_factory=dict)


class GenerationIn(BaseModel):
    provider: str = "demo"
    feedback: str = Field(default="", max_length=2000)
    refine: bool = False
    model: str = Field(default="", max_length=80)
    effort: str = Field(default="", max_length=20)

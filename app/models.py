from dataclasses import dataclass, field


@dataclass
class SearchResult:
    name: str
    pages: list[int] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return bool(self.pages)

    @property
    def pages_str(self) -> str:
        return ", ".join(map(str, self.pages)) if self.pages else "—"

    @property
    def count(self) -> int:
        return len(self.pages)

    @property
    def status_text(self) -> str:
        return "Encontrado" if self.found else "Não encontrado"

    @property
    def row_tag(self) -> str:
        return "found" if self.found else "not_found"

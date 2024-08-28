def enum(**enums):
    return type('Enum', (), enums)

Tenses = enum(PAST=0, PRESENT=1, FUTURE=3)
Pronouns = enum(I=0, YOU=1, HE=3, SHE=4, WE=5, YOUS=6, THEY=7)
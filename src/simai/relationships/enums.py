from enum import StrEnum


class RelationshipKind(StrEnum):
    FRIEND = "friend"
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    SIBLING_OF = "sibling_of"
    SPOUSE_OF = "spouse_of"
    EX_PARTNER_OF = "ex_partner_of"
    GRANDPARENT_OF = "grandparent_of"
    GRANDCHILD_OF = "grandchild_of"
    UNCLE_AUNT_OF = "uncle_aunt_of"
    NEPHEW_NIECE_OF = "nephew_niece_of"
    COUSIN_OF = "cousin_of"

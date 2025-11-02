
from sweetheart import verbose
from typing import Type,TypedDict,Literal,Optional


class TypeMeasure(TypeDict):
    """Base class for defining measure types."""
    name: str
    unit: Literal["kg","°Bx"]
    type: Type[int|float]

class Measure():

    type Valuation = Literal[
        "measure","constant","target","variable","unknown" ]

    def __init__(self, 
            measure_type: TypeMeasure,
            valuation: Valuation,
            key: str = None ):

        self.key = key or f"M.{measure.__name__}" #FIXME
        self.mtype = measure_type
        self.valuation = valuation
        self.value: Optional[measure_type.type] = None

    @classmethod
    def collection(cls, measures: list[Measure|Compute] )-> dict:
        return { m.key: m for m in measures }

class Compute():

    type Valuation = Literal[
        "once","fuzzy","recursive" ]

    def __init__(self,
            measure_type: TypeMeasure,
            valuation: Valuation,
            key: str = None ):

        self.key = key or f"C.{measure.__name__}" #FIXME
        self.mtype = measure_type
        self.valuation = valuation
        self.value: Optional[measure_type.type] = None

class BaseBlock:

    measures : list[TypeMeasure]
    computes : list[TypeMeasure]

    @classmethod
    def get_measures(cls)-> list[dict]:

        assert len(cls.measures)==len(set(cls.measures)),\
            "duplicated Measures in block definition forbidden"

        return "Ok",[{
            "name": measure.mtype.name,
            "unit": measure.mtype.unit,
            "type": measure.mtype.__name__
        } for measure in cls.measures ]
    
    @classmethod
    def get_computes(cls)-> list[dict]:

        assert len(cls.computes)==len(set(cls.computes)),\
            "duplicated Computes in block definition forbidden"

        return "Ok",[{
            "name": compute.mtype.name,
            "unit": compute.mtype.unit,
            "type": compute.mtype.__name__
        } for compute in cls.computes ]

    @classmethod
    def get_values(cls,max_index=4)-> dict:

        values = {}
        for index in range(max_index):

            #NOTE: max_index defines max number of In/Out collec
            i,o = f"In{index}",f"Out{index}"

            if hasattr(cls,i):
                # { "In1": { "M.GrossWeight": 100.0, ... }, ... }
                values[i] = {m.key: m.value for m in cls.__dict__[i]}
            if hasattr(cls,o):
                # { "Out1": { "M.GrossWeight": 100.0, ... }, ... }
                values[o] = {m.key: m.value for m in cls.__dict__[o]}

        return values

class FlowSheeting:

    name : str
    blocks : list[BaseBlock] = []
    restapi = {"GET": _GET_}

    @classmethod
    def append(cls,block:BaseBlock):
        """ Append a Block to the FlowSheeting. """

        cls.blocks.append(block)

        assert len(cls.blocks)==len(set(cls.blocks)),\
            "duplicated Blocks in FlowSheeting forbidden"

    @classmethod
    def _GET_(cls,d:dict)-> tuple[str,dict]:
        """ Respond to Rest API GET method. """

        index = cls.blocks.index(d["block"])
        block = cls.blocks[index]

        return "Ok",{
            "block": block.__name__,
            "measures": block.get_measures(),
            "computes": block.get_computes(),
            "values": block.get_values() }
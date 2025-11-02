""" Sweetheart's Measurement Library """

from sweetheart import verbose
from typing import Type,TypedDict,Literal,Optional,Self


class TypeMeasure(TypedDict):
    """Base class for defining measurement types."""
    name: str
    unit: Literal["kg","°Bx"]
    type: Type[int|float]


class Measure:
    """ Input Measurement. """

    type Valuation = Literal[
        "measurement","constant","target","variable","unknown" ]

    def __init__(self, 
            measure_type: TypeMeasure,
            valuation: Valuation,
            key: str = None ):

        self.key = key or f"M.{measure_type.__name__}" #FIXME
        self.mtype = measure_type
        self.valuation = valuation
        self.value: Optional[measure_type.type] = None

    @classmethod
    def collection(cls, measures: list[Self] )-> dict:
        return { m.key: m for m in measures }


class Compute:
    """ Computed Measurement. """

    type Valuation = Literal[
        "once","fuzzy","recursive" ]

    def __init__(self,
            measure_type: TypeMeasure,
            valuation: Valuation,
            key: str = None ):

        self.key = key or f"C.{measure_type.__name__}" #FIXME
        self.mtype = measure_type
        self.valuation = valuation
        self.value: Optional[measure_type.type] = None


class BaseBlock:

    def __init_subclass__(cls):

        cls.max_index = 4 #FIXME
        # cls.flowunit : FlowSheeting
        cls.measures : list[TypeMeasure]
        cls.computes : list[TypeMeasure]

        cls.flowunit.append(cls)

    @classmethod
    def get_measures(cls)-> list[dict]:

        assert len(cls.measures)==len(set(cls.measures)),\
            "duplicated Measures in block definition forbidden"

        return [{
            "name": measure.mtype.name,
            "unit": measure.mtype.unit,
            "type": measure.mtype.__name__
        } for measure in cls.measures ]
    
    @classmethod
    def get_computes(cls)-> list[dict]:

        assert len(cls.computes)==len(set(cls.computes)),\
            "duplicated Computes in block definition forbidden"

        return [{
            "name": compute.mtype.name,
            "unit": compute.mtype.unit,
            "type": compute.mtype.__name__
        } for compute in cls.computes ]

    @classmethod
    def get_values(cls)-> dict:

        values = {}
        for index in range(cls.max_index):

            #NOTE: max_index defines max number of In/Out collections
            i,o = f"In{index+1}",f"Out{index+1}"

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
    get_block = lambda bk: blocks[blocks.index[bk]]

    def __init__(self):
        # provide RestAPI methods to instances
        self.restapi = {"GET": FlowSheeting._GET_}

    @classmethod
    def _GET_(cls,d:dict)-> tuple[str,dict]:
        """ Respond to the RestAPI GET method. """

        block = cls.get_block(d["table"])

        return "Ok",{
            "block": block.__name__,
            "measures": block.get_measures(),# list[dict]
            "computes": block.get_computes(),# list[dict]   
            "values": block.get_values() # dict[str,dict]
        }
    
    @classmethod
    def append(cls,block:BaseBlock):
        """ Append a Block to FlowSheeting. """

        cls.blocks.append(block)

        assert len(cls.blocks)==len(set(cls.blocks)),\
            "duplicated Blocks in FlowSheeting forbidden"

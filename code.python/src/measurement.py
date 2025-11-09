""" Sweetheart's Measurement Library """

from sweetheart import verbose
from typing import Type,TypedDict,Literal,Optional,Self


class TypedMeasure(TypedDict):
    """Base class for defining measurement types."""
    name: str
    unit: Literal["kg","°Bx"]
    type: Type[int|float]


class Measure:
    """ Input Measurement. """

    type Valuation = Literal[
        "measurement","constant","target","variable","unknown" ]

    def __init__(self, 
            typed_measure: TypedMeasure,
            valuation: Valuation,
            default: Optional[int|float] = None ):

        self.key: str = f"M.{typed_measure.__name__}" #FIXME
        self.tmeasure: TypedMeasure = typed_measure
        self.valuation: str = valuation
        self.value: Optional[int|float] = default

    @staticmethod
    def collection(measures: list[Self] )-> list[dict]:
        return [{
            "key": m.key,
            "name": m.tmeasure.name,
            "unit": m.tmeasure.unit,
            "type": m.tmeasure.type.__name__,
            "value": m.value,
            "valuation": m.valuation } for m in measures ]

class Compute(Measure):
    """ Computed Measurement. """

    type Valuation = Literal[
        "once","fuzzy","recursive" ]

    def __init__(self, 
            typed_measure: TypedMeasure,
            valuation: Valuation ):

        super().__init__(typed_measure,valuation)
        self.key = f"C.{self.tmeasure.__name__}" #FIXME
        

class BaseBlock:

    def __init_subclass__(cls):

        cls.max_index = 4
        # cls.flowunit : FlowSheeting
        cls.measures : list[TypedMeasure]
        cls.computes : list[TypedMeasure]

        cls.flowunit.append(cls)

    @classmethod
    def get_measures(cls)-> list[dict]:

        assert len(cls.measures)==len(set(cls.measures)),\
            "duplicated Measures in block definition forbidden"

        return [{
            "key": f"M.{measure.__name__}", #FIXME
            "name": measure.name,
            "unit": measure.unit,
            "type": measure.type.__name__
        } for measure in cls.measures ]
    
    @classmethod
    def get_computes(cls)-> list[dict]:

        assert len(cls.computes)==len(set(cls.computes)),\
            "duplicated Computes in block definition forbidden"

        return [{
            "key": f"C.{compute.__name__}", #FIXME
            "name": compute.name,
            "unit": compute.unit,
            "type": compute.type.__name__
        } for compute in cls.computes ]

    @classmethod
    def get_values(cls)-> list[dict]:
        """ Return current In/Out measurement values. """
        
        values = []
        for index in range(cls.max_index):
            In, Out = f"In{index+1}", f"Out{index+1}"
            if hasattr(cls, In):
                values.insert(index,{ In: cls.__dict__[In] })
            if hasattr(cls, Out):
                values.append({ Out: cls.__dict__[Out] })

        return values
        

class FlowSheeting:

    name : str
    blocks : list[BaseBlock] = []

    def __init__(self, config=None):
        # provide RestAPI methods to instances
        self.restapi = {"GET": FlowSheeting._GET_}

    @classmethod
    def _GET_(cls,d:dict)-> tuple[str,dict]:
        """ Respond to the RestAPI GET method. """

        block = next(
            b for b in cls.blocks if b.__name__==d["table"] )

        return "Ok",{
            "block": block.__name__,
            "measures": block.get_measures(),
            "computes": block.get_computes(),
            "values": block.get_values() }

    @classmethod
    def append(cls,block:BaseBlock):
        """ Append a Block to FlowSheeting. """

        cls.blocks.append(block)

        assert len(cls.blocks)==len(set(cls.blocks)),\
            "duplicated Blocks in FlowSheeting forbidden"

""" Sweetheart's Measurement Library """

from sweetheart import verbose
from collections import UserDict
from typing import Type,TypedDict,Literal,Optional,Self


class TypedMeasure(TypedDict):
    """Base class for defining measurement types."""
    name: str
    unit: Literal["kg","°Bx","%","ICUMSA","bar","°C","kJ"]
    type: Type[int|float]


class Measure(UserDict):
    """ Input Measurement. """

    type Valuation = Literal[
        "measurement","constant","target","variable","unknown" ]

    def __init__(self, 
            typed_measure: TypedMeasure,
            valuation: Valuation,
            default: Optional[int|float] = None ):

        self.data = {
            "key": f"M.{typed_measure.__name__}",
            "name": typed_measure["name"],
            "unit": typed_measure["unit"],
            "type": typed_measure["type"].__name__,
            "init": default,
            "value": default,
            "valuation": valuation }

class Compute(Measure):
    """ Computed Measurement. """

    type Valuation = Literal[
        "once","fuzzy","recursive" ]

    def __init__(self, 
            typed_measure: TypedMeasure,
            valuation: Valuation ):

        super().__init__(typed_measure,valuation)
        self["key"] = f"C.{typed_measure.__name__}"
        

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
            "key": f"M.{measure.__name__}",
            "name": measure.name,
            "unit": measure.unit,
            "type": measure.type.__name__
        } for measure in cls.measures ]
    
    @classmethod
    def get_computes(cls)-> list[dict]:

        assert len(cls.computes)==len(set(cls.computes)),\
            "duplicated Computes in block definition forbidden"

        return [{
            "key": f"C.{compute.__name__}",
            "name": compute.name,
            "unit": compute.unit,
            "type": compute.type.__name__
        } for compute in cls.computes ]

    @classmethod
    def get_values(cls)-> list[dict]:
        """ Return current In/Out measurement values. """
        
        values = []
        measures = lambda io: cls.__dict__[io][1]

        for index in range(cls.max_index):
            In, Out = f"In{index+1}", f"Out{index+1}"
            if hasattr(cls, In): values.insert(index, {
                "id": In,
                "name": cls.__dict__[In][0],
                "values": [(m["key"],m["value"]) for m in measures(In)],
                # "valuation": [(m["key"],m["valuation"][0]) for m in measures(In)]
            })
            if hasattr(cls, Out): values.append({
                "id": Out,
                "name": cls.__dict__[Out][0],
                "values": [(m["key"],m["value"]) for m in measures(Out)],
                # "valuation": [(m["key"],m["valuation"][0]) for m in measures(Out)]
            })
        return values
        

class FlowSheeting:

    name : str
    flowenv : dict
    blocks : list[BaseBlock] = []

    @classmethod
    def append(cls,block:BaseBlock):
        """ Append a Block to FlowSheeting. """

        cls.blocks.append(block)

        assert len(cls.blocks)==len(set(cls.blocks)),\
            "duplicated Blocks in FlowSheeting forbidden"

    def __init__(self, config=None):
        # provide RestAPI methods to instances
        self.restapi = {
            "GET": FlowSheeting._GET_,
            "PATCH": FlowSheeting._PATCH_ }

    @classmethod
    def _GET_(cls,d:dict) -> tuple[str,dict]:
        """ Respond to the RestAPI GET method. """

        if d.get("origin") == "__flowsheet__":

            return "Ok",{
                "name": cls.__dict__.get("name","Unnamed FlowSheet"),#FIXME
                "blocks": [b.__name__ for b in cls.blocks] }

        elif d.get("origin") == "__block__":

            block = next(
                b for b in cls.blocks if b.__name__==d["dataset"] )

            return "Ok",{
                "block": block.__name__,
                "measures": block.get_measures(),
                "computes": block.get_computes(),
                "payload": block.get_values() }

    @classmethod
    def _PATCH_(cls,d:dict) -> tuple[str,None]:
        """ Respond to the RestAPI PATCH method. """

        assert len(d["payload"])==1,\
            "PATCH request must contain exactly one value."

        key,value = d["payload"].popitem()

        block: BaseBlock = next(
            b for b in cls.blocks
            if b.__name__ == d["dataset"] )

        measure: dict = next(
            i for i in getattr(block,d["id"])[1]
            if i["key"] == key )

        measure["value"] = value
        return "Ok", None

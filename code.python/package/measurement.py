""" Sweetheart's Measurement Library """

from sweetheart import verbose
from collections import UserDict,UserList
from typing import Type,TypedDict,Literal,Optional,Self,Callable,Iterable


class TypedMeasure(TypedDict):
    """ Base class for defining measurement types. """

    name: str
    unit: Literal["kg","°Bx","%","ICUMSA","bar","bara","°C","kJ"]
    type: Type[int|float]


class Measure(UserDict):
    """ Base class for building measurement instances. """

    type Valuation = Literal[
        "measurement","constant","target","variable","unknown" ]

    def __init__(self, 
            typed_measure: TypedMeasure,
            valuation: Valuation,
            formula: Optional[Callable] = None ):

        self.formula = formula
        super().__init__({
            "key": typed_measure.__name__,
            "name": typed_measure["name"],
            "unit": typed_measure["unit"],
            "type": typed_measure["type"].__name__,
            "init": None,
            "value": None,
            "valuation": valuation })

    def set(self, value: int|float):

        self["init"] = value
        self["value"] = value
        return self


class Compute(Measure):
    """ Base class for building computed measurement instances. """

    type Valuation = Literal[
        "once","fuzzy","recursive" ]

    def __init__(self,
            typed_measure: TypedMeasure,
            valuation: Valuation,
            formula: Callable ):
    
        super().__init__(typed_measure,valuation,formula)


class Flow(UserList):
    """ Build list grouping measurements related to a flow. """

    def __init__(self, iterable: Iterable[Measure|str]):

        self.__doc__ = next((
            i for i in iterable if isinstance(i,str)
            ), None)
        
        iterable.remove(self.__doc__)
        super().__init__(iterable)
        keys = [ measure["key"] for measure in self ]
    
        assert len(keys) == len(set(keys)),\
            "Duplicated measurements in Flow definition forbidden."

        [# set measurements as properties, e.g. Block.In1.Pressure()
            setattr(self,measure["key"],lambda m=measure: m["value"])
            for measure in self if isinstance(measure,Measure)
        ]

class Inlet(Flow):
    """ Build Flow instances defined as inlet. """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

class Outlet(Flow):
    """ Build Flow instances defined as outlet. """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)


class Balance(Flow):
    """ Build Flow-like instances for computing balances. """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

class Energy():
    pass


class BaseBlock:

    def __init_subclass__(cls):

        cls.max_index = 9
        # cls.flowunit : FlowSheeting
        cls.measures : list[TypedMeasure]
        cls.computes : list[TypedMeasure]

        if any([ 
            isinstance(getattr(cls,attr), Flow) 
            for attr in cls.__dict__ 
        ]): 
            # register block in flowsheeting
            cls.flowunit.append(cls)


class FlowSheeting:

    # list of registered blocks
    blocks : list[BaseBlock] = []
    iterations : int = 1000

    @classmethod
    def append(cls,block:BaseBlock):
        """ Append a Block to FlowSheeting. """

        cls.blocks.append(block)

        assert len(cls.blocks)==len(set(cls.blocks)),\
            "Duplicated Blocks in FlowSheeting forbidden."

    @classmethod
    def calculate(cls, iterations:Optional[int]=None):
        """ Execute computations in registered Blocks. """

        iterations = iterations or cls.iterations
        for _count_ in range(1, iterations+1):
            for block in cls.blocks:

                for flow in [ 
                    getattr(block,attr) for attr in block.__dict__ 
                    if isinstance(getattr(block,attr),Flow) ]:

                    for measure in flow:
                        if measure.get("unresolved",True) and measure.formula is not None:
                            try: 
                                match type(measure).__name__, measure["valuation"]:

                                    case "Measure", "measurement":
                                        measure["value"] = measure.formula()
                                    
                                    # case "Measure", "constant":
                                    #     assert measure["value"] is not None,\
                                    #         "Constant measures must be set."

                                    case "Measure", "target":
                                        offset = 0.01  # 1% tolerance
                                        measure["value"] = measure.formula()

                                        if measure["value"] < (1-offset) * measure["init"] \
                                        or measure["value"] > (1+offset) * measure["init"]:
                                            measure["unresolved"] = True

                                    case "Measure", "variable":
                                        raise NotImplementedError

                                    case "Measure", "unknown":
                                        raise NotImplementedError

                                    case "Compute", "once":
                                        measure["value"] = measure.formula()
                                        measure["unresolved"] = False

                                    case "Compute", "fuzzy":
                                        raise NotImplementedError

                                    case "Compute", "recursive":
                                        measure["value"] = measure.formula()

                            except:
                                measure["unresolved"] = True

                            finally:
                                if measure.get("unresolved") and _count_ == iterations:
                                    raise ValueError("Unresolved measure after maximum iterations.")


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
                "flowsheet": cls.__doc__,
                "blocks": [b.__name__ for b in cls.blocks] }

        elif d.get("origin") == "__block__":

            block = next(
                b for b in cls.blocks 
                if b.__name__ == d["dataset"] )

            sorted_inouts = sorted([   
                attr for attr in block.__dict__ 
                if isinstance(getattr(block,attr),Flow) 
            ], key= lambda x: ('InFlOu'.index(x[:2]),x[2:]) )

            return "Ok",{
                            "blockname": block.__name__,
                            "blockdoc": block.__doc__,

                            "measures": [
                                {
                                    "key": measure.__name__,
                                    "name": measure.name,
                                    "unit": measure.unit,
                                    "type": measure.type.__name__
                                } for measure in block.measures
                            ],
                            "computes": [
                                {
                                    "key": compute.__name__,
                                    "name": compute.name,
                                    "unit": compute.unit,
                                    "type": compute.type.__name__
                                } for compute in block.computes
                            ],
                            "inouts": [
                                {
                                    "key": inout,
                                    "name": getattr(block,inout).__doc__
                                } for inout in sorted_inouts
                            ],
                            "payload": [
                                # build list of (id,value) tuples
                                (f"{inout}::{measure['key']}", measure["value"])
                                for inout in sorted_inouts
                                for measure in getattr(block,inout)
                            ] 
                        }

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

    @classmethod
    def __PUT__(cls,d:dict) -> tuple[str,None]:
        """ Respond to the RestAPI PUT method. """
        pass




# --- --- Legacy --- --- #

 # @classmethod
    # def get_measures(cls)-> list[dict]:

    #     assert len(cls.measures)==len(set(cls.measures)),\
    #         "duplicated Measures in block definition forbidden"

    #     return [{
    #         "key": f"M.{measure.__name__}",
    #         "name": measure.name,
    #         "unit": measure.unit,
    #         "type": measure.type.__name__
    #     } for measure in cls.measures ]
    
    # @classmethod
    # def get_computes(cls)-> list[dict]:

    #     assert len(cls.computes)==len(set(cls.computes)),\
    #         "duplicated Computes in block definition forbidden"

    #     return [{
    #         "key": f"C.{compute.__name__}",
    #         "name": compute.name,
    #         "unit": compute.unit,
    #         "type": compute.type.__name__
    #     } for compute in cls.computes ]

    # @classmethod
    # def get_InOuts(cls)-> list[str]:
    #     """ Return current In/Out measurement points. """

    #     InOuts = []
    #     for index in range(cls.max_index):

    #         In, Out = f"In{index+1}", f"Out{index+1}"

    #         if hasattr(cls,In): InOuts.insert(index,{
    #             "key": In,
    #             "name": getattr(cls,In)[0] })

    #         if hasattr(cls,Out): InOuts.append({
    #             "key": Out,
    #             "name": getattr(cls,Out)[0] })

    #     return InOuts

    # @classmethod
    # def get_values(cls)-> list[dict]:
    #     """ Return current In/Out measurement values. """
        
    #     values = []
    #     for inout in [ io["key"] for io in cls.get_InOuts() ]:
    #         for m in getattr(cls,inout)[1]:
    #             _id = f"{inout}::{m['key']}"
    #             values.append((_id, m["value"]))

    #     return values

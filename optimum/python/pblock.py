
from sweetheart.measures import \
    TypeMeasure,Measure,Compute,BaseBlock,FlowSheeting


# --- --- Measure Types --- --- #

class GrossWeight(TypeMeasure):
    name = "Poids Brut"
    unit = "kg"
    type = float

class Brix(TypeMeasure):
    name = "BRIX"
    unit = "°Bx"
    type = float


# --- --- Flowsheetings --- --- #

class ProcessUnit(FlowSheeting):
    # routable with DataHub("/data",ProcessUnit())
    name = "Generic Process Unit"
    

# --- --- Process Blocks --- --- #

class ExchangerBlock(BaseBlock):

    # Block Definition

    flowunit : FlowSheeting = ProcessUnit
    flowunit.append("ExchangerBlock")

    measures : list[TypeMeasure] = [
        GrossWeight, Brix ]

    computes : list[TypeMeasure] = [
        GrossWeight, Brix ]

    # Inlet / Outlet Definitions

    In1 = Measure.collection(
        [
            Measure(GrossWeight,"constant"),
            Measure(Brix,"unknown"),

            Compute(GrossWeight,"once"),
            Compute(Brix,"fuzzy")
        ])

    Out1 = Measure.collection(
        [
            Measure(GrossWeight,"variable"),
            Measure(Brix,"target"),

            Compute(GrossWeight,"recursive"),
            Compute(Brix,"once")
        ])
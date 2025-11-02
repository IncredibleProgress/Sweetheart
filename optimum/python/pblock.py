
from sweetheart.measurement import \
    TypeMeasure,Measure,Compute,BaseBlock,FlowSheeting


# --- --- Measurement Types --- --- #

class GrossWeight(TypeMeasure):
    name = "Poids Brut"
    unit = "kg"
    type = float

class Brix(TypeMeasure):
    name = "BRIX"
    unit = "°Bx"
    type = float


# --- --- Flow Sheetings --- --- #

class ProcessUnit(FlowSheeting):
    # routable with DataHub("/data",ProcessUnit())
    name = "Single Process Unit"
    

# --- --- Process Blocks --- --- #

class ExchangerBlock(BaseBlock):

    # Set Block Definition

    flowunit : FlowSheeting = ProcessUnit

    measures : list[TypeMeasure] = [
        GrossWeight, Brix ]

    computes : list[TypeMeasure] = [
        GrossWeight, Brix ]

    # Set Inlet / Outlet Definitions

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

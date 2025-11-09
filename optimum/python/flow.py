
from sweetheart.measurement import \
    TypedMeasure,Measure,Compute,BaseBlock,FlowSheeting


# --- --- Measurement Types --- --- #

class GrossWeight(TypedMeasure):
    name = "Poids Brut"
    unit = "kg"
    type = float

class Brix(TypedMeasure):
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

    measures : list[TypedMeasure] = [
        GrossWeight, Brix ]

    computes : list[TypedMeasure] = [
        GrossWeight, Brix ]

    # Set Inlet / Outlet Definitions

    In1 = Measure.collection(
        [
            Measure(GrossWeight,"constant",1000.0),
            Measure(Brix,"unknown",12.0),

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

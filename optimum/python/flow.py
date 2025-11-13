
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
    """ List blocks composing a process unit. """

    name = "Process Unit"


class ProcessBlocks(BaseBlock):
    """ Blocks group sharing same flowunit, measures, computes. """

    flowunit : FlowSheeting = ProcessUnit

    measures : list[TypedMeasure] = [
        GrossWeight, Brix ]

    computes : list[TypedMeasure] = [
        GrossWeight, Brix ]
    

# --- --- Process Blocks --- --- #

class ExchangerBlock(ProcessBlocks):

    In1 =\
    [
        Measure(GrossWeight,"constant",1000.0),
        Measure(Brix,"unknown",12.0),
        Compute(GrossWeight,"once"),
        Compute(Brix,"fuzzy")
    ]

    Out1 =\
    [
        Measure(GrossWeight,"variable"),
        Measure(Brix,"target"),
        Compute(GrossWeight,"recursive"),
        Compute(Brix,"once")
    ]

    In2 =\
    [
        Measure(GrossWeight,"constant",1000.0),
        Measure(Brix,"unknown",12.0),
        Compute(GrossWeight,"once"),
        Compute(Brix,"fuzzy")
    ]

    Out2 =\
    [
        Measure(GrossWeight,"variable"),
        Measure(Brix,"target"),
        Compute(GrossWeight,"recursive"),
        Compute(Brix,"once")
    ]

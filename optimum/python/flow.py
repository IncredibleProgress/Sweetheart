
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

class Purity(TypedMeasure):
    name = "Pureté"
    unit = "%"
    type = float

class Colorimetry(TypedMeasure):
    name = "Colorimétrie"
    unit = "ICUMSA"
    type = float

class Pressure(TypedMeasure):
    name = "Pression"
    unit = "bar"
    type = float

class Temperature(TypedMeasure):
    name = "Température"
    unit = "°C"
    type = float

class Rate(TypedMeasure):
    name = "Ratio"
    unit = "%"
    type = float

class DryMatter(TypedMeasure):
    name = "MS"
    unit = "%"
    type = float

class Energy(TypedMeasure):
    name = "Énergie"
    unit = "J"
    type = float

class Enthalpy(TypedMeasure):
    name = "Enthalpie"
    unit = "kJ"
    type = float

class SaturationTemp(TypedMeasure):
    name = "Temp.Sat."
    unit = "°C"
    type = float


# --- --- Flow Sheetings --- --- #

class ProcessUnit(FlowSheeting):
    """ List blocks composing a process unit. """

    name = "Test Unit"


class ProcessBlocks(BaseBlock):
    """ Blocks group sharing same flowunit, measures, computes. """

    flowunit : FlowSheeting = ProcessUnit

    measures : list[TypedMeasure] = [
        GrossWeight, Brix, Purity, Pressure, Temperature ]

    computes : list[TypedMeasure] = [
        Rate, DryMatter, Energy, Enthalpy, SaturationTemp ]
        

# --- --- Process Blocks --- --- #

class ExchangerBlock(ProcessBlocks):

    In1 = "Entrée jus cru",
    [
        Measure(GrossWeight,"constant",10.0),
        Measure(Brix,"unknown",10.0),
        Measure(Purity,"unknown",85.0),
        Measure(Pressure,"unknown",2.0),
        Measure(Temperature,"unknown",25.0),
        Compute(Rate,"once"),
        Compute(DryMatter,"fuzzy"),
        Compute(Energy,"once"),
        Compute(Enthalpy,"once"),
        Compute(SaturationTemp,"once")
    ]

    Out1 = "Sortie jus réchauffé",
    [
        Measure(GrossWeight,"variable"),
        Measure(Brix,"target"),
        Measure(Pressure,"unknown",2.0),
        Measure(Temperature,"unknown",25.0),
        Compute(Rate,"once"),
        Compute(DryMatter,"fuzzy"),
        Compute(Energy,"once"),
        Compute(Enthalpy,"once"),
        Compute(SaturationTemp,"once")
    ]

    In2 = "Entrée eau chaude",
    [
        Measure(GrossWeight,"constant",1000.0),
        Measure(Brix,"unknown",12.0),
        Compute(GrossWeight,"once"),
        Compute(Brix,"fuzzy")
    ]

    Out2 = "Sortie eau refroidie",
    [
        Measure(GrossWeight,"variable"),
        Measure(Brix,"target"),
        Compute(GrossWeight,"recursive"),
        Compute(Brix,"once")
    ]

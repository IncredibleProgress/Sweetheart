
from sweetheart.measurement import (
    TypedMeasure, Measure, Compute, 
    FlowSheeting, BaseBlock, Flow, Inlet, Outlet)


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


# --- --- Flow Sheeting --- --- #

class ProcessUnit(FlowSheeting):
    "Test Unit Flowsheeting"


class ProcessBlock(BaseBlock):

    flowunit : FlowSheeting = ProcessUnit

    measures : list[TypedMeasure] = [
        GrossWeight, Brix, Purity, Pressure, Temperature ]

    computes : list[TypedMeasure] = [
        Rate, DryMatter, Energy, Enthalpy, SaturationTemp ]
    

# --- --- Process Blocks --- --- #

# @register("Ex",globals)
class ExchangerBlock(ProcessBlock):
    "Échangeur thermique"

    In1 = Inlet([
        "Entrée jus froid",

        Measure(GrossWeight,"constant").set(1000.0),
        Measure(Brix,"unknown"),
        Measure(Purity,"unknown"),
        Measure(Pressure,"unknown"),
        Measure(Temperature,"unknown"),

        Compute(Rate,"once",lambda: Ex.In1.GrossWeight() / 100.0),
        # Compute(DryMatter,"fuzzy"),
        # Compute(Energy,"once"),
        # Compute(Enthalpy,"once"),
        # Compute(SaturationTemp,"once")
    ])

    # Out1 = "Sortie jus réchauffé",\
    # [
    #     Measure(GrossWeight,"variable"),
    #     Measure(Brix,"target"),
    #     Measure(Pressure,"unknown",2.0),
    #     Measure(Temperature,"unknown",25.0),
        
    #     Compute(Rate,"once"),
    #     Compute(DryMatter,"fuzzy"),
    #     Compute(Energy,"once"),
    #     Compute(Enthalpy,"once"),
    #     Compute(SaturationTemp,"once")
    # ]

    # In2 = "Entrée eau chaude",[
    #     Measure(GrossWeight,"constant",1000.0),
    #     Measure(Brix,"unknown",12.0),
    #     Compute(GrossWeight,"once"),
    #     Compute(Brix,"fuzzy")]

    # Out2 = "Sortie eau refroidie",[
    #     Measure(GrossWeight,"variable"),
    #     Measure(Brix,"target"),
    #     Compute(GrossWeight,"recursive"),
    #     Compute(Brix,"once")]


# class MixerBlock(BaseBlock,ProcessBlocks):

#     In1 = "Entrée sirop",[
#         Measure(GrossWeight,"constant",500.0),
#         Measure(Brix,"unknown",65.0),
#         Compute(GrossWeight,"once"),
#         Compute(Brix,"fuzzy")]

#     In2 = "Entrée eau",[
#         Measure(GrossWeight,"constant",2000.0),
#         Measure(Brix,"unknown",5.0),
#         Compute(GrossWeight,"once"),
#         Compute(Brix,"fuzzy")]

#     Out1 = "Sortie mélange",[
#         Measure(GrossWeight,"variable"),
#         Measure(Brix,"target"),
#         Compute(GrossWeight,"once"),
#         Compute(Brix,"fuzzy")]


# --- --- Formula Lexicon --- --- #

Ex = ExchangerBlock
ProcessUnit.calculate()
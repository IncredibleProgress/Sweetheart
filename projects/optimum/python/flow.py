
from sweetheart.measurement import (
    TypedMeasure, Measure, Compute, 
    FlowSheeting, BaseBlock, Flow, Inlet, Outlet, Balance)


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

    iterations = 1000


class ProcessBlock(BaseBlock):

    flowunit : FlowSheeting = ProcessUnit

    measures : list[TypedMeasure] = [
        GrossWeight, Brix, Purity, Pressure, Temperature ]

    computes : list[TypedMeasure] = [
        Rate, DryMatter, Energy, Enthalpy, SaturationTemp ]
    

# --- --- Process Blocks --- --- #

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

    In2 = Inlet([
        "Entrée eau chaude",

        Measure(GrossWeight,"constant").set(500.0),
        Measure(Brix,"unknown").set(70.0),

        # Compute(GrossWeight,"once"),
        # Compute(Brix,"fuzzy")
    ])

    Out1 = Outlet([
        "Sortie jus réchauffé",

        Measure(GrossWeight,"variable").set(500.0),
        Measure(Brix,"target"),
        Measure(Pressure,"unknown"),
        Measure(Temperature,"unknown"),
        
        # Compute(Rate,"once"),
        # Compute(DryMatter,"fuzzy"),
        # Compute(Energy,"once"),
        # Compute(Enthalpy,"once"),
        # Compute(SaturationTemp,"once")
    ])

    Out2 = Outlet([
        "Sortie eau refroidie",

        Measure(GrossWeight,"variable"),
        Measure(Brix,"target"),

        # Compute(GrossWeight,"recursive"),
        # Compute(Brix,"once")
    ])

    Ba1 = Balance([
        "Bilan jus réchauffé",

        Compute(Enthalpy,"once",lambda: 0.01, ),

        # Alert("GrossWeight negative",lambda:\
        #     Ex.Bn1.GrossWeight() < 0.0 )
    ])

    
class MixerBlock(ProcessBlock):
    "Mélangeur sirop"

    In1 = Inlet([
        "Entrée sirop",
        Measure(GrossWeight,"constant"),
        Measure(Brix,"unknown"),
        # Compute(GrossWeight,"once"),
        # Compute(Brix,"fuzzy")
    ])

    In2 = Inlet([
        "Entrée eau",
        Measure(GrossWeight,"constant"),
        Measure(Brix,"unknown"),
        # Compute(GrossWeight,"once"),
        # Compute(Brix,"fuzzy")
    ])

    Out1 = Outlet([
        "Sortie mélange",
        Measure(GrossWeight,"variable"),
        Measure(Brix,"target"),
    #     Compute(GrossWeight,"once"),
    #     Compute(Brix,"fuzzy")
    ])

# --- --- Formula Lexicon --- --- #

Ex = ExchangerBlock
ProcessUnit.calculate()

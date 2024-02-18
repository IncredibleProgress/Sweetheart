// Maintenance App Refactory

import React from 'react'
import '../resources/tailwind.css'
import { render,MiniApp,Title,TextInput,SelectOption,TextArea } from './components'

const prior = ['P0','P1','P2','P3','P4']
const categ = ['SECU','FOOD','MTCE']
const owner = ['MECA','ELEC','CHAU','SYST']

render(<MiniApp>
  
  <Title className="text-center">
    Demande d'intervention
  </Title>

  <div>
    <SelectOption options={prior}/>
    <SelectOption options={categ}/>
  </div>

  <div>
    <TextInput className="w-full"
      placeholder="Quel est le problème ?"/>
  </div>

  <div className="flex">
    <TextInput className="w-full" placeholder="équipement"/>
    <TextInput className="w-24 text-center" placeholder="criticité" disabled/>
    <SelectOption options={owner}/>
  </div>

  <TextArea className="w-full min-h-48" 
    placeholder="donnez toutes les informations utiles"/>

</MiniApp>)
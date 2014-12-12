#! usr/bin/python
# -*- coding: utf-8 -*-

####
##  Copyright © 2010 CIML
##
##  This file is part of WormBase Converter.
##
##  WormBase Converter is free software: you can redistribute it  
##  and/or modify it under the terms of the GNU General Public License  
##  as published by the Free Software Foundation, either version 3 of 
##  the License, or (at your option) any later version.
##
##  WormBase Converter is distributed in the hope that it will be 
##  useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
##  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License
##  along with WormBase Converter. If not, see <http://www.gnu.org/licenses/>.
####

import ConfigParser


class MyConfigParser (ConfigParser.ConfigParser):
    
    filename = ""
    
    def __init__ (self, filename):
        self.filename = filename
        ConfigParser.ConfigParser.__init__(self)
        ConfigParser.ConfigParser.read(self, self.filename)
    
    def set(self, section, option, value):
        ConfigParser.ConfigParser.set(self, section, option, value)
        ConfigParser.ConfigParser.write(self, open(self.filename, 'w'))

    def setboolean(self, section, option, value):
        try :
            if (bool(value) == True) :
                self.set(section, option, 'True')
            else :
                self.set(section, option, 'False')
        except :
            self.set(section, option, 'False')
            
            

def get_WB_releases_installed (freezes_only = False, all = False):
    '''Renvoie la liste des versions de WormBase ou de EASE installées dans l'ordre décroissant.
       freezes_only = False : Renvoie toutes les versions
                    = True : Renvoie uniquement les versions "Freezes" (toutes les 10 versions)
       all = False : Renvoie les n° des versions uniquement
           = True : Renvoie les n° des versions et les noms des fichiers correspondants.'''
    
    releases = {'num' : [],                       # n° des versions
                'files' : []}                     # fichiers correspondants
    
        # Récupère les versions installées
    CFG = MyConfigParser('config.ini')
    releases_installed = CFG.get('WORMBASE', 'releases')
    releases_installed = releases_installed.split(',')
    
        # Enregistre les versions (toutes/freezes uniquement)
    if (releases_installed != ['']) :
		for release in releases_installed :
		    release = int(release)
		    if ((freezes_only == False) or (release % 10  == 0)) :
		        releases['num'].append(release)
		        if (all == True) : releases['files'].append('geneIDs.WS' + str(release))
      
        # Tri dans l'ordre décroissant (release la plus récente en priorité)
    releases['num'].reverse()
    releases['files'].reverse()
    
  
        # Renvoi du résultat
    if (all == False) : return releases['num']
    else : return releases



def get_geneIDs (release, IDs = ['gene', 'wb', 'cgc']):
    '''Renvoie la liste des gènes présents dans une version donnée de WormBase.
       release = n° de la version de WormBase
       IDs[] = "gene" : renvoie la liste des Gene ID (Sequence Name Gene)
               "wb" : renvoie la liste des WormBase ID (WBGene ID)
               "cgc" : renvoie la liste des noms des gènes (Gene Name)'''

        # Récupère la liste des gènes
    results = {'gene' : [],                   # liste Sequence Name Gene
               'wb' : [],                     # liste WormBase ID
               'cgc' : []}                    # liste Gene Name
    

        # Récupère la liste des versions installées, et les fichiers correspondants
    releases_installed = get_WB_releases_installed(all=True)


        # Vérifie que la version demandée est bien installée
    if release not in releases_installed['num'] :
        if 'gene' not in IDs : del results['gene']
        if 'wb' not in IDs : del results['wb']
        if 'cgc' not in IDs : del results['cgc']
        return results              # renvoie dictionnaire vide


        # Récupère les listes de gènes (différents ID)
    filename = 'geneIDs.WS' + str(release)

    f = open('wormbase/geneIDs/' + filename, 'r')
    
    line = f.readline()
    while (line != "") :
        line = line.strip().split(',')
        
            # Enregistre uniquement les IDs souhaités
        if 'gene' in IDs : results['gene'].append(line[2])
        if 'wb' in IDs : results['wb'].append(line[0])
        if 'cgc' in IDs : results['cgc'].append(line[1])
        
        line = f.readline()

    f.close()


        # Renvoi du résultat
    if 'gene' not in IDs : del results['gene']
    if 'wb' not in IDs : del results['wb']
    if 'cgc' not in IDs : del results['cgc']
    
    return results



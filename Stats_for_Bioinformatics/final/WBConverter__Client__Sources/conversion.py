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

from Tkinter import *
import ttk, operator
import utils


class Conversion :


    class Error (Exception):
        def __init__(self, errno, strerror):
            self.errno = errno
            self.strerror = strerror
        def __str__(self):
            return repr(self.strerror)
    

    def __init__ (self):
        pass



    def detect_IDs (self, gene_list):
        """Recherche les différents identifiants présents dans une liste de gènes :
                - 'gene' : Gene Sequence Name
                - 'cds' : CDS Sequence Name
                - 'transcript' : Transcript Sequence Name
                - 'wb' : WormBase ID
                - 'cgc' : Gene Name
           gene_list = [] : Liste des gènes"""

        IDs = [] 
        
        for gene in gene_list :
            if (gene[0:2] == 'WB') : IDs.append('wb')
            elif (gene.count('.') == 2) : IDs.append('transcript')
            elif (gene.count('.') == 1) and (gene[-1].isalpha() == True) : IDs.append('cds')
            elif (gene.count('.') == 1) and (gene.find("-") == -1) : IDs.append('gene')
            else : IDs.append('cgc')
            
        return list(set(IDs))



    def separate_IDs (self, gene_list):
        """Sépare la liste de gènes en catégorie, selon leur identifiant :
                - 'gene' : Gene Sequence Name
                - 'cds' : CDS Sequence Name
                - 'transcript' : Transcript Sequence Name
                - 'wb' : WormBase ID
                - 'cgc' : Gene Name
           gene_list = [] : Liste des gènes"""
   
        genes = {'wb' : [], 'cgc' : [], 'gene' : [], 'cds' : [], 'transcript' : []}
   
        for gene in gene_list :
            if (gene[0:2] == 'WB') : genes['wb'].append(gene)
            elif (gene.count('.') == 2) : genes['transcript'].append(gene)
            elif (gene.count('.') == 1) and (gene[-1].isalpha() == True) : genes['cds'].append(gene)
            elif (gene.count('.') == 1) and (gene.find("-") == -1) : genes['gene'].append(gene)
            else : genes['cgc'].append(gene)
            
        return genes



    def convert_CDS_to_GeneID (self, gene_list = []):
        """Convertit une liste de gènes de CDS Sequence Name en Gene Sequence Name.
           gene_list = [] : Liste des gènes"""
        
            # Supprime la marque des isoformes (a, b, c, ..)
        for i in range(len(gene_list)) :
            if (gene_list[i].count('.') == 1) and (gene_list[i][-1].isalpha() == True) :
                gene_list[i] = gene_list[i][:-1]

        return gene_list
    
    
    
    def convert_Transcript_to_GeneID (self, gene_list = []):
        """Convertit une liste de gènes de Transcript Sequence Name en Gene Sequence Name (en supprimant également les CDS Sequence Name intermédiaires).
           gene_list = [] : Liste des gènes"""
        
            # Supprime la marque des transcrits (.1, .2, .3, ...)
        for i in range(len(gene_list)) :
            if (gene_list[i].count('.') == 2) :
                gene_list[i] = gene_list[i][:gene_list[i].rfind('.')]
        
            # Supprime la marque des isoformes (a, b, c, ..)
        self.convert_CDS_to_GeneID(gene_list)
        
        return gene_list



    def convert_GeneIDs (self, gene_list, release, input_ID, output_ID):
        """Convertit une liste de gènes d'un identifiant vers un autre identifiant.
           gene_list = [] : Liste des gènes
           release : Release WormBase utilisée dans la liste de gènes
           input_ID : Identifiant utilisé dans la liste de gène
           output_ID : Identifiant souhaité après la conversion"""
        
        converted = []                          # liste des gènes convertis (en input_ID)
        no_synonym = []                         # liste des gènes convertis mais aucun résultat lors de la conversions  (en input_ID)
        unconverted = []                        # liste des gènes impossibles à convertir (non présents dans la release)  (en input_ID)
        results = []                            # liste des gènes convertis (en output_ID)

            # Récupère la liste des gènes (uniquement les ID input & output) de la version
        geneIDs = utils.get_geneIDs(release, [input_ID, output_ID])
            
            # Convertit la liste des gènes
        for gene in gene_list :
            
            try :
                index = geneIDs[input_ID].index(gene)               # essaie de trouver le gène dans la liste
                gene_converted = geneIDs[output_ID][index]          # si présent, conversion du gène
                if (gene_converted != "") :
                    converted.append(gene)                          # gène avec synonyme
                    results.append(gene_converted)
                elif (gene_converted == "") :
                    no_synonym.append(gene)                         # gène sans synonyme
            except :
                unconverted.append(gene)                            # si non présent, pas de conversion
                
        return {'converted' : converted, 'unconverted' : unconverted, 'no_synonym' : no_synonym, 'results' : results}


    
    def detect_release (self, win_parent = None, gene_list = [], releases_list = [], IDs = ['wb', 'cgc', 'gene']):
        """Recherche la(les) version(s) de WormBase correspondante(s) à  la liste de gènes donnée.
            win_parent : Fenêtre parente (None si en ligne de commande)
            gene_list = [] : Liste des gènes
            releases_list = [] : Liste des releases installées
            IDs = [] : Identifiants utilisés dans la liste de gènes ('wb' = WB ID, 'cgc' = Gene Name, 'gene' = Gene Sequence Name)"""

        class __Detect_Release :
            """Recherche la(les) version(s) de WormBase correspondante(s) à  la liste de gènes donnée."""
            
            __win_parent = None                     # fenêtre parente (None si en ligne de commande
            __gene_list = []                        # liste des gènes
            __releases_list = []                    # liste des releases à étudier
            __IDs = []                              # identifiants utilisés dans la liste de gènes ['wb', 'cgc', 'gene']
            
            __release = None                        # release la plus probable après analyse
        
        
            def __init__ (self, win_parent, gene_list, releases_list, IDs):
                self.__win_parent = win_parent
                self.__gene_list = gene_list
                self.__releases_list = releases_list
                self.__IDs = IDs
                self.__release = None
                              
                
            def __get_best_releases_freeze (self) :
                    # Récupère uniquement les versions freeze (toutes les 10)
                releases_freeze = []
                for release in self.__releases_list :
                    if (release % 10 == 0) :
                        releases_freeze.append(release)
                        
                    # Calcul le % de gènes dans les releases freeze
                res = self.__calcul_pourcent(releases_freeze)
                    
                    # Tri du résultat par le % le plus grand, puis par la version la plus récente
                res.sort(key=operator.itemgetter(1,0))
                res.reverse()

                    # On récupère les 2 meilleures releases freeze                
                return res[:2]
                
            
            
            def __calcul_pourcent (self, releases_list) :
                result = []
                
                for release in releases_list :
                    
                        # Récupère la liste des tous les IDs souhaités (SeqName Gene, WB ID, Gene Name) de la version
                    geneIDs = utils.get_geneIDs(release, self.__IDs)
                    
                        # Décompte le nombre de gènes de la liste retrouvés dans la version
                    qte = 0
                    if 'wb' in self.__IDs : qte = qte + len([x for x in self.__gene_list if (x in geneIDs['wb'])])
                    if 'gene' in self.__IDs : qte = qte + len([x for x in self.__gene_list if (x in geneIDs['gene'])])
                    if 'cgc' in self.__IDs : qte = qte + len([x for x in self.__gene_list if (x in geneIDs['cgc'])])
                    
                        # Enregistrement du %
                    result.append([release, float(qte)/len(self.__gene_list)*100])
                    
                return result
            
            
        
            def detect_release (self):
            
                    # Recherche les 2 releases freeze où le % de correspondance est le meilleur
                best_freeze = self.__get_best_releases_freeze()

                    # Calcul le % de gènes dans les releases intermédiaires
                releases_list = []
                for i in range(min(best_freeze[0][0], best_freeze[1][0]), max(best_freeze[0][0], best_freeze[1][0])+1) :
                    releases_list.append(i)
                    
                pourcent_inter = self.__calcul_pourcent (releases_list[1:-1])
                
                    # Tri du résultat par le % le plus grand, puis par la version la plus récente
                pourcent_inter = pourcent_inter + best_freeze
                pourcent_inter.sort(key=operator.itemgetter(1,0))
                pourcent_inter.reverse()
                pourcent_inter = pourcent_inter[:5]                                             # sélection des 5 meilleurs résultats
                
                    # On sélectionne la meilleure release, si elle est unique à 100%
                if (pourcent_inter[0][1] == 100) and (pourcent_inter[1][1] < 100) :
                    return pourcent_inter[0][0]
                
                    # Sinon, on demande à l'utilisteur de choisir
                else :
                        # affichage graphique
                    if (self.__win_parent != None) :
                        self.__window_candidates(pourcent_inter)
                        while (self.__release == None) : self.__win_parent.update()             # Boucle d'attente
                        return self.__release
            
                        # retour de la liste des 5 meilleures releases, si en ligne de commande
                    else :
                        return pourcent_inter
        
        
            def __window_candidates (self, candidates) :
                    
                def __quit ():
                    self.__release = int(release_best_candidate.get().split()[1])
                    win_candidates.destroy()                
                    
                def __pass ():
                    pass
                    
                    # Création de la liste des releases possibles
                aff_candidates = []
                for candidate in candidates :
                    aff_candidates.append("WS %3d   (%6.2f%%)" % (candidate[0], candidate[1]))
                    
                    # Création de la fenêtre
                win_candidates = Toplevel(self.__win_parent)
                win_candidates.title('Release candidates')
                win_candidates.resizable(width=False, height=False)
                    
                    # Objets
                Label(win_candidates, text='Choose the correct release :').pack(side=TOP, padx=10, pady=5, fill=X)
                    
                release_best_candidate = StringVar()
                ttk.Combobox(win_candidates, values=aff_candidates, textvariable=release_best_candidate, width=16, state='readonly').pack(side=TOP, padx=10, pady=5)
                    
                Button(win_candidates, text="OK", width=10, command=__quit).pack(side=BOTTOM, padx=10, pady=5)
                
                    # Release par défaut, la plus proche de 100%
                release_best_candidate.set(aff_candidates[0])
                
                win_candidates.protocol("WM_DELETE_WINDOW", __pass)
            

            # Elimine les lignes vides dans la liste des gènes
        no_value = []
        for i in range(len(gene_list)) :
            if (gene_list[i] == "") : no_value.append(i)
        for i in no_value :
            gene_list.pop(i)

            # Vérification des arguments
        if (len(gene_list) == 0) or (len(releases_list) == 0) or (len(IDs) == 0) :
            raise self.Error(1, 'Empty argument')

            # Recherche la(les) meilleure(s) release(s) possible(s)
        instance = __Detect_Release(win_parent, gene_list, releases_list, IDs)
        release = instance.detect_release()
        return release



    def update_geneIDs (self, WB_gene_list, input_release, resurrected_list = False):
        """Met à jour une liste de gènes (en WormBase ID) vers la version directement supérieure (release + 1).
           WB_gene_list : Liste des gènes (en WormBase ID)
           input_release : Release de la liste de gènes
           resurrected_list = True | False : Renvoie (ou non) la liste des gènes ressuscités entre les versions"""       
        
        new_gene_list = []
        
            # Enregistrement des évolutions dans le nom des gènes entre les 2 versions
        gene_del = {'old' : [], 'new' : []}                 # gènes supprimés après Merge ou Split
        gene_new = {'old' : [], 'new' : []}                 # gènes ajoutés après Split From
        gene_killed = []                                    # gènes totalement supprimés
        gene_resurrected = []                               # gènes réapparus
        
        try :
            f_evol = open('wormbase/geneEvols/WS' + str(input_release) + '-WS' + str(input_release + 1), 'rb')
        except :
            raise self.Error(2, 'FileEvols not found : "%s"' % ('wormbase/geneEvols/WS' + str(input_release) + '-WS' + str(input_release + 1)))
        
        evol = f_evol.readline()
        while (evol != "") :
            evol = evol.strip().split()
            
            if (evol[1] == "DEL") and ((evol[2] == "Merged_into") or (evol[2] == "Split_into")) :
                gene_del['old'].append(evol[0])
                gene_del['new'].append(evol[3])
                
            elif (evol[1] == "DEL") :               # Killed , Made_into_transposon + les inversions de dates Killed/Imported
                gene_killed.append(evol[0])
        
            elif (evol[1] == "NEW") and (evol[2] == "Split_from") :
                gene_new['old'].append(evol[3])
                gene_new['new'].append(evol[0])
                
            elif (evol[1] == "NEW") and (evol[2] == "Resurrected") :
                gene_resurrected.append(evol[0])
                
            evol = f_evol.readline()
        
        f_evol.close()

        
            # MAJ du nom des gènes
        for gene in WB_gene_list :
            gene_infos = []                                     # informations sur les changements dans le nom du gène
            gene_infos.append(gene)                             # .. nom du gène initial

            if gene in gene_del['old'] :
                for i in range(gene_del['old'].count(gene)) :
                    gene_infos.append('Merged/Split to')        # .. évolution DEL = Merged / Split to
                    index = gene_del['old'].index(gene)
                    gene_infos.append(gene_del['new'][index])   # nouvel ID
                    gene_del['old'].pop(index)                  # on supprime le changement du gène dans la liste, pour ne pas qu'il soit repris à la boucle 'for' suivante
                    gene_del['new'].pop(index)                  # idem
                    new_gene_list.append(gene_infos)            # enregistre les changements [[ancien ID, évolution, nouvel ID], ..]
                    gene_infos = []
                    gene_infos.append(gene)
        
            elif gene in gene_new['old'] :
                gene_infos.append('Split from')                 # on garde le gène à l'origine du split
                gene_infos.append(gene)                         # ..
                new_gene_list.append(gene_infos)
                gene_infos = []
                gene_infos.append(gene)
                
                for i in range(gene_new['old'].count(gene)) :
                    gene_infos.append('Split from')             # .. évolution NEW = Split from
                    index = gene_new['old'].index(gene)
                    gene_infos.append(gene_new['new'][index])
                    gene_new['old'].pop(index)
                    gene_new['new'].pop(index)
                    new_gene_list.append(gene_infos)
                    gene_infos = []
                    gene_infos.append(gene)
        
            elif gene in gene_killed :
                gene_infos.append('Killed')                     # .. évolution KILLED
                gene_infos.append('')
                new_gene_list.append(gene_infos)
        
            else :
                gene_infos.append('No change')                  # .. évolution NO CHANGE
                gene_infos.append(gene)
                new_gene_list.append(gene_infos)
            
            
            # Renvoi du résultat
        if (resurrected_list == False) : return new_gene_list
        else : return [new_gene_list, gene_resurrected]



    def downdate_geneIDs (self, WB_gene_list, input_release, killed_list = False):
        """Met à jour une liste de gènes (en WormBase ID) vers la version directement inférieure (release - 1).
           WB_gene_list : Liste des gènes (en WormBase ID)
           input_release : Release de la liste de gènes
           killed_list = True | False : Renvoie (ou non) la liste des gènes supprimés entre les versions"""     

        new_gene_list = []
        
            # Enregistrement des évolutions dans le nom des gènes entre les 2 versions
        gene_del_merged = {'old' : [], 'new' : []}          # gènes supprimés après Merge
        gene_del_split = {'old' : [], 'new' : []}           # gènes supprimés après Split
        gene_new = {'old' : [], 'new' : []}                 # gènes ajoutés après Split From
        gene_created = []                                   # gènes apparus
        gene_killed = []                                    # gènes supprimés
        
        try :
            f_evol = open('wormbase/geneEvols/WS' + str(input_release - 1) + '-WS' + str(input_release), 'rb')
        except :
            raise self.Error(2, 'FileEvols not found : "%s"' % ('wormbase/geneEvols/WS' + str(input_release - 1) + '-WS' + str(input_release)))
        
        evol = f_evol.readline()
        while (evol != "") :
            evol = evol.strip().split()
            
            if (evol[1] == "DEL") and (evol[2] == "Merged_into") :
                gene_del_merged['old'].append(evol[0])
                gene_del_merged['new'].append(evol[3])                
            
            elif (evol[1] == "DEL") and (evol[2] == "Split_into") :
                gene_del_split['old'].append(evol[0])
                gene_del_split['new'].append(evol[3])
                
            elif (evol[1] == "DEL") :               # Killed , Made_into_transposon + les inversions de dates Killed/Imported
                gene_killed.append(evol[0])
                
            elif (evol[1] == "NEW") and (evol[2] == "Split_from") :
                gene_new['old'].append(evol[3])
                gene_new['new'].append(evol[0])
                
            elif (evol[1] == "NEW") and ((evol[2] == "Created") or (evol[2] == "Imported") or (evol[2] == "Resurrected")) :
                gene_created.append(evol[0])
                
            evol = f_evol.readline()
        
        f_evol.close()

        
            # MAJ du nom des gènes
        for gene in WB_gene_list :
            gene_infos = []                                     # informations sur les changements dans le nom du gène
            gene_infos.append(gene)                             # .. nom du gène initial


            if gene in gene_del_merged['new'] :
                for i in range(gene_del_merged['new'].count(gene)) :
                    gene_infos.append('Merged (reverse)')       # .. évolution INVERSE DEL MERGED
                    index = gene_del_merged['new'].index(gene)
                    gene_infos.append(gene_del_merged['old'][index])
                    gene_del_merged['new'].pop(index)
                    gene_del_merged['old'].pop(index)
                    new_gene_list.append(gene_infos)
                    gene_infos = []
                    gene_infos.append(gene)
                gene_infos.append('Merged (reverse)')           # ajoute le gène lui-même
                gene_infos.append(gene)                         # lorsqu'il y a fusion
                new_gene_list.append(gene_infos)
                gene_infos = []
                gene_infos.append(gene)
            
            elif gene in gene_del_split['new'] :
                gene_infos.append('Split to (reverse)')         # .. évolution INVERSE DEL SPLIT TO
                index = gene_del_split['new'].index(gene)
                gene_infos.append(gene_del_split['old'][index])
                new_gene_list.append(gene_infos)
            
            elif gene in gene_new['new'] :
                for i in range(gene_new['new'].count(gene)) :
                    gene_infos.append('Split from (reverse)')   # .. évolution INVERSE DEL SPLIT FROM
                    index = gene_new['new'].index(gene)
                    gene_infos.append(gene_new['old'][index])
                    gene_new['new'].pop(index)
                    gene_new['old'].pop(index)
                    new_gene_list.append(gene_infos)
                    gene_infos = []
                    gene_infos.append(gene)

            elif gene in gene_created :
                gene_infos.append('Created/Resurrected (reverse)')   # .. évolution INVERSE CREATED
                gene_infos.append('')
                new_gene_list.append(gene_infos)          

            else :
                gene_infos.append('No change')                  # .. évolution NO CHANGE
                gene_infos.append(gene)
                new_gene_list.append(gene_infos)
                
            
            # Renvoi du résultat
        if (killed_list == False) : return new_gene_list
        else : return [new_gene_list, gene_killed]           
           
           


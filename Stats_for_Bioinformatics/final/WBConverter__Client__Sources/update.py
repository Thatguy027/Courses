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

import ConfigParser, ftplib, urllib, os, subprocess, time, threading
import re, gzip, datetime, operator


class MyConfigParser (ConfigParser.ConfigParser):
    """Modification du module 'ConfigParser' pour permettre l'enregistrement en temps réel des modifications."""
    
    filename = ""
    
    def __init__ (self, filename):
        self.filename = filename
        ConfigParser.ConfigParser.__init__(self)
        ConfigParser.ConfigParser.read(self, self.filename)
    
    def set(self, section, option, value):
        """Enregistre une valeur dans une clé d'une section donnée.
           section / option / value : Section / Clé / Valeur souhaitée"""
    
        ConfigParser.ConfigParser.set(self, section, option, value)
        ConfigParser.ConfigParser.write(self, open(self.filename, 'w'))

    def setboolean(self, section, option, value):
        """Enregistre une valeur au format boolean dans une clé d'une section donnée.
           section / option / value : Section / Clé / Valeur souhaitée"""
    
        try :
            if (bool(value) == True) :
                self.set(section, option, 'True')
            else :
                self.set(section, option, 'False')
        except :
            self.set(section, option, 'False')
            





class FTP_Connection :
    """Classe permettant la communication avec un serveur FTP distant."""
    
    host = ""
    login = ""
    password = ""       
    
    cnx = None


    def __init__ (self) :
        pass


    def connection (self, host, login, password):
        """Connexion à un serveur FTP distant.
           host : Adresse de l'hôte
           login & password : Login et mot de passe utilisé pour se connecter au serveur"""
            
            # Sauvegarde des informations de connexion
        self.host = host
        self.login = login
        self.password = password            
                        
        if (login == "") :
            self.cnx = ftplib.FTP(self.host)
        elif (password == "") :
            self.cnx = ftplib.FTP(self.host, self.login)
        else :
            self.cnx = ftplib.FTP(self.host, self.login, self.password)

        return self.cnx



    def disconnection (self):
        """Déconnexion d'un serveur FTP."""
        
            # Teste si la connexion FTP est toujours active
        try :
            self.cnx.quit()
        except :
            pass



    def list_files (self, directory) :
        """Liste tous les fichiers présents dans un répertoire du serveur FTP.
           directory : Chemin du répertoire"""
           
           # Teste si la connexion est toujours active
        try :
            self.cnx.pwd()
        except :
            self.connection(self.host, self.login, self.password)
                           
            # Récupère tous les éléments dans le répertoire
        all = self.__get_all_elements_in_directory(directory)

            # Ne sélectionne que les fichiers
        files = []

        for element in all :
            if (element[0] == '-') : files.append(element.split()[8])

        return files



    def list_directories (self, directory) :
        """Liste tous les dossiers présents dans un répertoire du serveur FTP.
           directory : Chemin du répertoire"""
                
           # Teste si la connexion est toujours active
        try :
            self.cnx.pwd()
        except :
            self.connection(self.host, self.login, self.password)                
                
            # Récupère tous les éléments dans le répertoire
        all = self.__get_all_elements_in_directory(directory)

            # Ne sélectionne que les fichiers
        directories = []

        for element in all :
            if (element[0] == 'd') : directories.append(element.split()[8])

        return directories



    def __get_all_elements_in_directory (self, directory) :
        """Liste tous les éléments (dossiers, fichiers, liens, ...) présents dans un répertoire du serveur FTP.
           directory : Chemin du répertoire"""

        all = []
        self.cnx.cwd(directory)
        self.cnx.dir(all.append)             # enregistrement des éléments dans all[]

        return all



    def download_file (self, ftp_path, ftp_filename, local_dest):
        """Télécharge un fichier à partir d'un serveur FTP.
           ftp_path : Chemin du répertoire où se trouve le fichier à télécharger (sur le serveur FTP)
           ftp_filename : Nom du fichier à télécharger
           local_dest : Chemin et Nom du fichier où sera téléchargé le fichier"""
                
           # Teste si la connexion est toujours active
        try :
            self.cnx.pwd()
        except :
            self.connection(self.host, self.login, self.password)                
                
        try :
            f = open(local_dest, 'wb')                              # ouverture du fichier de destination en écriture
                    
            self.cnx.cwd(ftp_path)                                  # changement du répertoire courant
            self.cnx.retrbinary('RETR ' + ftp_filename, f.write)    # téléchargement du fichier
                    
            f.close()
        except :
            raise

        f = open(local_dest, 'rb')
        bin = f.read(1024)
        f.close()

        if (bin == "") :
            raise
        else :
            return local_dest
            
            
            
            
            
            
class Update_WormBase :
    """Classe permettant de gérer les mises à jours de WormBase."""


    CFG = None                          # Configuration / Options
    LANG = None                         # Langue utilisée
    
    __update_running = False            # Mise à jour de WormBase en cours
    __force_to_quit = False             # Forcer l'arrêt de la MAJ
    __process_update = None             # Processus de MAJ
    __process_result = False            # Etat du processus après son arrêt (True : normal ; False : Processus interrompu)

    __server_info_downloaded = False    # Fichier d'information du serveur téléchargé ?



    def __init__ (self, CFG_filename, LANG_filename) :
        self.CFG = MyConfigParser(CFG_filename)
        self.LANG = MyConfigParser(LANG_filename)



    def __del__ (self) :
        """Force l'arrêt d'une mise à jour avant destruction de la classe."""
    
        self.stop_update_WormBase()



    def error (self, msg, fatal = False) :
        """Affiche (ou enregistre dans un fichier) une erreur, et remet à zéro la classe si besoin.
           msg : Texte à afficher (ou enregistrer)
           fatal = True | False : Détermine si la classe doit être remise à zéro"""
    
        print "# " + msg
        
            # RAZ
        if (fatal == True) :
        
                # Arrête la MAJ
            if (self.__process_update != None) :
                self.__process_update.kill()
        
            self.__update_running = False
            self.__force_to_quit = False
            self.__process_update = None        
            self.__process_result = False
            self.CFG.set('UPDATE', 'running', 'False')
            


    def __download_server_file (self, path, filename):
        """Télécharge un fichier situé sur le serveur dans le dossier temporaire (temp/).
           path : Répertoire du serveur où est présent le fichier à télécharger 
           filename : Nom du fichier à télécharger"""
    
            # Télécharge le fichier
        if (path[-1] != '/') : path = path + '/'
        try :
            urllib.urlretrieve(path + filename, 'temp/' + filename)
        except :
            return False
        
            # Vérifie que le téléchargement est correct
        f = open('temp/' + filename, 'rb')
        line = f.readline().strip()
        if (line == '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">') :
            f.close()
            os.remove('temp/' + filename)
            return False
        else :
            f.close()
            return True



    def check_server_info (self, obj_statusbar, check_update, check_param) :
        """Met à jour l'ordinateur Client (par rapport au serveur).
           obj_satatusbar : Barre de status de l'application (permet de visualiser l'avancement et les erreurs)
           check_update = True | False : Recherche les nouvelles versions de WormBase disponibles
           check_param = True | False : Met à jour les paramètres utilisés pour les mises à jour"""

        time.sleep(1)

        res = True
        if (check_param == True) :
            res = self.__check_parameters(obj_statusbar)

        if (check_update == True) and (res == True) :
            self.__check_update(obj_statusbar)
            
            

    def __check_update (self, obj_statusbar) :
        """Recherche et installe les mises-à-jour du seveur sur l'ordinateur client."""
        
            # Télécharge les informations du serveur
        res = True
        if (self.__server_info_downloaded == False) :
            obj_statusbar.config(text=self.LANG.get('UPDATER', 'download_server_info'))
            res = self.__download_server_file(self.CFG.get('UPDATE', 'server_host'), 'config.ini')
        
        if (res == False) :
            obj_statusbar.config(text=self.LANG.get('UPDATER', 'download_server_info_error'))
            return False        
        else :
            self.__server_info_downloaded = True
        
        
            # Récupère la liste des releases disponibles
        obj_statusbar.config(text=self.LANG.get('UPDATER', 'get_server_new_releases'))
        server_CFG = MyConfigParser('temp/config.ini')
        releases_available = server_CFG.get('WORMBASE', 'releases')
        releases_available = releases_available.split(',')
        releases_available = [int(release) for release in releases_available]
        
        
            # Récupère la liste des releases installées
        releases_installed = self.CFG.get('WORMBASE', 'releases')
        releases_installed = releases_installed.split(',')
        releases_installed = [int(release) for release in releases_installed if (release != '')]       
       
       
            # Récupère la liste des releases à installer ou réinstaller(suite à une modification manuelle/correction)
        releases_list = [release for release in releases_available if release not in releases_installed]
            
        releases_forced = server_CFG.get('UPDATE', 'force')
        if (releases_forced != "") :
            releases_forced = releases_forced.split(',')
            releases_forced = [int(release) for release in releases_forced]
        else :
            releases_forced = []
        
        releases_list = releases_list + releases_forced


            # Installation des nouvelles releases
        new_installed = []
        for release in releases_list :
        
                # Téléchargement des geneIDs
            obj_statusbar.config(text=self.LANG.get('UPDATER', 'download_geneIDs') % release)
            res = self.__download_server_file(self.CFG.get('UPDATE', 'server_host') + 'wormbase/geneIDs', 'geneIDs.WS' + str(release))
            if (res == False) :
                obj_statusbar.config(text=self.LANG.get('UPDATER', 'download_geneIDs_error') % release)
                continue 

                # Téléchargement des évolutions par rapport à la version précédente
            obj_statusbar.config(text=self.LANG.get('UPDATER', 'download_evols') % (release-1,release))
            res = self.__download_server_file(self.CFG.get('UPDATE', 'server_host') + 'wormbase/geneEvols/', 'WS' + str(release-1) + '-WS' + str(release))
            
            # si erreur due à l'absence du fichier d'évolution pour la toute première release
            if (res == False) and (release == min(releases_available)) :
            
                    # Déplacement des fichiers téléchargés dans les bons dossiers (installation)
                obj_statusbar.config(text=self.LANG.get('UPDATER', 'install_new_release') % release)
                fr = open('temp/geneIDs.WS' + str(release), 'rb')
                fw = open('wormbase/geneIDs/geneIDs.WS' + str(release), 'wb')
                fw.write(fr.read())
                fw.close()
                fr.close()
                
                    # Suppression des fichiers téléchargés (du répertoire temporaire)
                os.remove('temp/geneIDs.WS' + str(release)) 
                
                new_installed.append(release)
                continue
                
            # autre erreur
            elif (res == False) :
                obj_statusbar.config(text=self.LANG.get('UPDATER', 'download_evols_error') % (release-1,release))
                continue     
                
                # Déplacement des fichiers téléchargés dans les bons dossiers (installation)
            obj_statusbar.config(text=self.LANG.get('UPDATER', 'install_new_release') % release)
            fr = open('temp/geneIDs.WS' + str(release), 'rb')
            fw = open('wormbase/geneIDs/geneIDs.WS' + str(release), 'wb')
            fw.write(fr.read())
            fw.close()
            fr.close()
        
            fr = open('temp/WS' + str(release-1) + '-WS' + str(release), 'rb')
            fw = open('wormbase/geneEvols/WS' + str(release-1) + '-WS' + str(release), 'wb')
            fw.write(fr.read())
            fw.close()
            fr.close()

                # Suppression des fichiers téléchargés (du répertoire temporaire)
            os.remove('temp/geneIDs.WS' + str(release)) 
            os.remove('temp/WS' + str(release-1) + '-WS' + str(release))
            
            new_installed.append(release)


            # Ajout des releases installées dans le fichier de configuration
        new_installed__str = ""
        for release in new_installed :
            if (release not in releases_installed) :
                new_installed__str = new_installed__str + ',' + str(release)
            
        if (len(releases_installed) == 0) :
            self.CFG.set('WORMBASE', 'releases', self.CFG.get('WORMBASE', 'releases') + new_installed__str[1:])
        else :
            self.CFG.set('WORMBASE', 'releases', self.CFG.get('WORMBASE', 'releases') + new_installed__str)

            # Message d'erreur ou de confirmation
        if (new_installed != releases_list) :
            releases_not_installed = [str(release) for release in releases_list if release not in new_installed]
            
            not_installed_str = ""
            for release in releases_not_installed :
                not_installed_str = not_installed_str + str(release) + ','
            
            obj_statusbar.config(text=self.LANG.get('UPDATER', 'update_from_server_error') % not_installed_str[:-1])

        else :
            if (len(new_installed) != 0) and (new_installed != releases_forced) and (len(releases_installed) != 0):
                obj_statusbar.config(text=self.LANG.get('UPDATER', 'install_new_release_complete') % new_installed__str[1:])
            else :
                obj_statusbar.config(text=self.LANG.get('UPDATER', 'up_to_date'))
        

        return True
      

    
    def __check_parameters (self, obj_statusbar) :
        """Enregistre les nouveaux paramètres du serveur sur l'ordinateur client."""
        
            # Télécharge les informations du serveur
        res = True
        if (self.__server_info_downloaded == False) :
            obj_statusbar.config(text=self.LANG.get('UPDATER', 'download_server_info'))
            res = self.__download_server_file(self.CFG.get('UPDATE', 'server_host'), 'config.ini')
        
        if (res == False) :
            obj_statusbar.config(text=self.LANG.get('UPDATER', 'download_server_info_error'))
            return False
        else :
            self.__server_info_downloaded = True
            
            # Récupère tous les paramètres du serveur (en écrasant les anciens)
        obj_statusbar.config(text=self.LANG.get('UPDATER', 'get_server_param'))
        server_CFG = MyConfigParser('temp/config.ini')
        
        param= {'server_host' : server_CFG.get('UPDATE', 'server_host'),
                'auto_correct' : server_CFG.get('UPDATE', 'auto_correct'),
                'save_update_log' : server_CFG.get('UPDATE', 'save_update_log'), 
                'save_acedb_file' : server_CFG.get('UPDATE', 'save_acedb_file'), 
                
                'ftp_host' : server_CFG.get('UPDATE', 'ftp_host'), 
                'ftp_port' : server_CFG.get('UPDATE', 'ftp_port'), 
                'ftp_login' : server_CFG.get('UPDATE', 'ftp_login'), 
                'ftp_password' : server_CFG.get('UPDATE', 'ftp_password'), 
                'ftp_regexp' : server_CFG.get('UPDATE', 'ftp_regexp'),
                
                'db_host' : server_CFG.get('UPDATE', 'db_host'), 
                'db_port' : server_CFG.get('UPDATE', 'db_port'), 
                'db_login' : server_CFG.get('UPDATE', 'db_login'), 
                'db_password' : server_CFG.get('UPDATE', 'db_password'), 
                
                'letter_host' : server_CFG.get('UPDATE', 'letter_host'), 
                'letter_port' : server_CFG.get('UPDATE', 'letter_port'), 
                'letter_login' : server_CFG.get('UPDATE', 'letter_login'), 
                'letter_password' : server_CFG.get('UPDATE', 'letter_password'), 
                'letter_regexp' : server_CFG.get('UPDATE', 'letter_regexp')}
        
            # Enregistre tous les paramètres
        obj_statusbar.config(text=self.LANG.get('UPDATER', 'save_server_param'))
        self.save_parameters (param, 'SERVER_Admin')
        
        obj_statusbar.config(text=self.LANG.get('UPDATER', 'save_server_param_done'))   
        return True
             
    
    
    def send_parameters (self, param) :
        """Envoi les nouveaux paramètres de MAJ au serveur."""
        
            # Récupère l'adresse du serveur
        host = self.CFG.get('UPDATE', 'server_host')
        
            # Paramètres à envoyer au serveur
        parameters = {'action' : 'PARAMETERS_WORMBASE',
                      'param' : param}
        
            # Envoie d'une demande de MAJ du serveur
        data = urllib.urlencode(parameters)
        f = urllib.urlopen(host + 'launcher.php', data)   
    
    
    
    def save_parameters (self, param, access) :
        """Enregistre les paramètres.
           param : Dictionnaire contenant les paramètres dans un format spécifique
           total_access = 'LOCAL' | 'SERVER_Admin' | 'SERVER_Client' : Détermine les droits de modification des paramètres"""

# DESCRIPTION DU DICTIONNAIRE 'param' A PASSER EN ARGUMENT ::
#
#        param= {'server_host' : None,
#                'auto_correct' : None,
#                'save_update_log' : None, 
#                'save_acedb_file' : None, 
#                
#                'ftp_host' : None, 
#                'ftp_port' : None, 
#                'ftp_login' : None, 
#                'ftp_password' : None, 
#                'ftp_regexp' : None,
#                
#                'db_host' : None, 
#                'db_port' : None, 
#                'db_login' : None, 
#                'db_password' : None, 
#                
#                'letter_host' : None, 
#                'letter_port' : None, 
#                'letter_login' : None, 
#                'letter_password' : None, 
#                'letter_regexp' : None}
        
        
            # Enregistrement du serveur FTP (pour les installations SERVEUR)
        if (access == 'LOCAL') :
            self.CFG.set('UPDATE', 'server_host', "LOCAL installation")
#        elif (access == 'SERVER_Admin') :
#            if (param['server_host'][:7] != "http://") : self.CFG.set('UPDATE', 'server_host', "http://" + param['server_host'])  
#            else : self.CFG.set('UPDATE', 'server_host', param['server_host'])
            
            
        if (access == 'LOCAL') or (access == 'SERVER_Admin') :

                # Enregistrement des options
            self.CFG.setboolean('UPDATE', 'auto_correct', param['auto_correct']) 
            self.CFG.setboolean('UPDATE', 'save_update_log', param['save_update_log']) 
            self.CFG.setboolean('UPDATE', 'save_acedb_file', param['save_acedb_file'])            

                # Enregistrement des informations sur le serveur FTP
            self.CFG.set('UPDATE', 'ftp_host', param['ftp_host'])        
            self.CFG.set('UPDATE', 'ftp_port', param['ftp_port'])  
            self.CFG.set('UPDATE', 'ftp_login', param['ftp_login'])  
            self.CFG.set('UPDATE', 'ftp_password', param['ftp_password'])  
            self.CFG.set('UPDATE', 'ftp_regexp', param['ftp_regexp'])  

                # Enregistrement des informations sur la base de données
            self.CFG.set('UPDATE', 'db_host', param['db_host'])
            self.CFG.set('UPDATE', 'db_port', param['db_port'])
            self.CFG.set('UPDATE', 'db_login', param['db_login'])
            self.CFG.set('UPDATE', 'db_password', param['db_password'])  

                # Enregistrement des informations sur la "letter"
            self.CFG.set('UPDATE', 'letter_host', param['letter_host'])        
            self.CFG.set('UPDATE', 'letter_port', param['letter_port'])  
            self.CFG.set('UPDATE', 'letter_login', param['letter_login'])  
            self.CFG.set('UPDATE', 'letter_password', param['letter_password'])  
            self.CFG.set('UPDATE', 'letter_regexp', param['letter_regexp'])  
            
    
    
    def ask_update_server (self) :
        """Envoi une demande de mise-à-jour au serveur."""
        
            # Récupère l'adresse du serveur
        host = self.CFG.get('UPDATE', 'server_host')
        
            # Paramètres à envoyer au serveur
        parameters = {'action' : 'UPDATE_WORMBASE',
                      'param' : ""}
        
            # Envoie d'une demande de MAJ du serveur
        data = urllib.urlencode(parameters)
        f = urllib.urlopen(host + 'launcher.php', data)  
        
    

    def stop_update_WormBase (self) :
        """Arrête la mise à jour de WormBase dès que possible."""

        if (self.__update_running == True) :
        
                # Arrête la MAJ
            if (self.__process_update != None) :
                self.__process_update.kill()
                
            self.__force_to_quit = True
        


    def get_run_status (self) :
        """Retourne l'état du script (MAJ de WormBase en cours ?)."""
    
        return self.__update_running
        


    def update_WormBase (self) :
        """Met à jour les versions de WormBase."""
    
        def __check_new_releases (FTP):
            """Recherche les nouvelles release disponibles (non installées).
               FTP : Instance de la classe FTP_Connection"""

            def __format_regexp (regexp) :

                beg = regexp.find('<release>')
                end = regexp.rfind('/', 0, beg)

                directory = regexp[:end+1]
                regexp = '^' + regexp[end+1:].replace('<release>', '([0-9]+)')

                return (directory, regexp)


            def __list_files_match (all_files, regexp):
                
                releases = []
                
                regexp = re.compile(regexp)             # Création de l'expression régulière
                
                    # Enregistrement des versions
                for f in all_files :
                    v = regexp.findall(f)               # Recherche les éléments validant l'expression régulière
                    if (len(v) != 0) :
                        releases.append(int(v[0]))
                
                return releases


            def __get_releases_installed ():
                
                    # Récupère la liste des releases installées
                releases_installed = self.CFG.get('WORMBASE', 'releases')
                releases_installed = releases_installed.split(',')
                
                    # Conversion en Int
                for i in range(len(releases_installed)) :
                    releases_installed[i] = int(releases_installed[i])
            
                return releases_installed


                # Formate l'expression régulière pour récupérer le nom du dossier et l'expression régulière des fichiers de GeneIDs
            directory, regexp = __format_regexp(self.CFG.get('UPDATE', 'ftp_regexp'))

                # Récupère la liste des fichiers contenant les GeneIDs de toutes les versions
            all_files = FTP.list_files(directory)

                # Sélectionne uniquement les fichiers correspondant à l'expression régulière
            releases_available = __list_files_match (all_files, regexp)

                # Récupère la liste des releases déjà installées
            releases_installed = __get_releases_installed()

                # Sélectionne les releases qui n'ont pas été installées
            new_releases = [release for release in releases_available if (release not in releases_installed)]

            return new_releases



        def __get_GeneIDs (FTP, release) :
            """Récupère les GeneIDs d'une version de WormBase.
               FTP : Instance de la classe FTP_Connection
               release : version [int] de WormBase"""

            def __format_regexp (regexp, release) :

                beg = regexp.find('<release>')
                end = regexp.rfind('/', 0, beg)

                directory = regexp[:end+1]
                filename = regexp[end+1:].replace('<release>', str(release)).replace('\\', '')

                return (directory, filename)


            def __decompress_file (src, dest):
                
                f_gz = gzip.open(src, 'rb')                             # ouverture de l'archive (lecture)
                f_txt = open(dest, 'wb')                                # ouverture du fichier de destination
                
                f_txt.write(f_gz.read())                                # décompression de l'archive dans le fichier de destination
                
                f_txt.close()
                f_gz.close()


                # Formate l'expression régulière pour récupérer les noms du dossier et du fichier à télécharger pour une release
            directory, filename = __format_regexp(self.CFG.get('UPDATE', 'ftp_regexp'), release)

                # Téléchargement de l'archive contenant le fichier avec les GeneIDs   
            print "      " + self.LANG.get('UPDATER', 'progress_download')
            FTP.download_file(directory, filename, 'wormbase/temp/' + filename)
            
                # Décompression de l'archive pour récupérer le fichier contenant les GeneIDs
            print "      " + self.LANG.get('UPDATER', 'progress_extraction')
            __decompress_file('wormbase/temp/' + filename, 'wormbase/temp/geneIDs.WS' + str(release))



        def __create_diff_file (old_release, new_release) :
            """Crée un fichier contenant la liste des gènes ajoutés ou supprimés entre 2 versions de WormBase.
               old_release & new_release : Versions de WormBase à utiliser pour la comparaison des gènes"""

            def __get_gene_list (file):

                gene_list = []
                
                f = open(file, 'rb')
                line = f.readline()
                while (line != "") :
                    line = line.strip().split(',')
                    gene_list.append(line[0])
                    line = f.readline()
                f.close()

                return gene_list


                # Récupère la liste des gènes des deux releases (l'une insatllée, l'autre non)
            try :
                gene_list_1 = set(__get_gene_list('wormbase/geneIDs/geneIDs.WS' + str(old_release)))
                gene_list_2 = set(__get_gene_list('wormbase/temp/geneIDs.WS' + str(new_release)))
            except :
                return -1
            
                # Création des listes des gènes supprimés ou ajoutés entre les versions
            deleted = gene_list_1 - gene_list_2
            deleted = list(deleted)

            created = gene_list_2 - gene_list_1
            created = list(created)

                # Création d'un fichier des différences (suppressions, ajouts) entre les 2 versions
            f_diff = open('wormbase/temp/diff_WS' + str(old_release) + '-WS' + str(new_release), 'wb')
            
            for gene in deleted :
                f_diff.write(gene + '\t' + 'DEL' + '\r\n')
                
            for gene in created :
                f_diff.write(gene + '\t' + 'NEW' + '\r\n')
                
            f_diff.close()
            
            return len(deleted + created)



        def __get_changes (old_release, new_release, recur = False) :
            """Récupère toutes les modifications apportées à la liste des gènes entre 2 versions de WormBase.
               old_release & new_release : Versions de WormBase à utiliser pour la comparaison des gènes
               (recur est utilisé pour la récursivité automatiquement)"""


            def __get_ACeDB_info () :
            
                    # Création du fichier ACeDB (si non existant)
                f = open('wormbase/temp/ACeDB_WS' + str(old_release) + '-WS' + str(new_release), 'ab')
                f.close()
            
                    # Recherche des modifications (appel du script PERL pour communiquer avec la BDD)
                if (self.CFG.getboolean('UPDATE', 'save_update_log') == True) :
                    f = open('wormbase/temp/UPDATE_LOG_ACeDB.txt', 'ab')
                    f.write("\n*** " + str(datetime.date.today()) + " (AAAA-MM-DD) ***\n")
                    f.close()                
                
                    f = open('wormbase/temp/UPDATE_LOG_ACeDB.txt', 'ab')
                    
                    if (os.path.exists('get_history.pl') == True) :
                        self.__process_update = subprocess.Popen(['perl', 'get_history.pl', 'diff_WS' + str(old_release) + '-WS' + str(new_release), self.CFG.get('UPDATE', 'db_host'),
                                                                  self.CFG.get('UPDATE', 'db_port'), self.CFG.get('UPDATE', 'db_login'), self.CFG.get('UPDATE', 'db_password')],
                                                                  stdout=f)
                    else :
                        self.__process_update = subprocess.Popen(['get_history.exe', 'diff_WS' + str(old_release) + '-WS' + str(new_release), self.CFG.get('UPDATE', 'db_host'),
                                                                  self.CFG.get('UPDATE', 'db_port'), self.CFG.get('UPDATE', 'db_login'), self.CFG.get('UPDATE', 'db_password')])
                                          
                    self.__process_update.wait()                                                              
                                                              
                    f.close()
                
                else :
                    if (os.path.exists('get_history.pl') == True) :
                        self.__process_update = subprocess.Popen(['perl', 'get_history.pl', 'diff_WS' + str(old_release) + '-WS' + str(new_release), self.CFG.get('UPDATE', 'db_host'),
                                                                  self.CFG.get('UPDATE', 'db_port'), self.CFG.get('UPDATE', 'db_login'), self.CFG.get('UPDATE', 'db_password')])
                    else :
                        self.__process_update = subprocess.Popen(['get_history.exe', 'diff_WS' + str(old_release) + '-WS' + str(new_release), self.CFG.get('UPDATE', 'db_host'),
                                                                  self.CFG.get('UPDATE', 'db_port'), self.CFG.get('UPDATE', 'db_login'), self.CFG.get('UPDATE', 'db_password')])
  
                    self.__process_update.wait()


                    # Vérifie si la récupération des modifications s'est déroulée correctement
                try :
                    f = open('wormbase/temp/ACeDB_WS' + str(old_release) + '-WS' + str(new_release) + '.errors', 'rb')
                    f.close()
                except :            # = aucune erreur
                    return True
                else :              # = présence d'erreurs
                    return False


            def __create_new_diff_files_from_errors () :
          
                    # Récupère la liste des gènes où une erreur est survenue
                errors = []       
         
                f_errors = open('wormbase/temp/ACeDB_WS' + str(old_release) + '-WS' + str(new_release) + '.errors', 'rb')
                line = f_errors.readline()
                while (line != "") :
                    errors.append(line.strip())
                    line = f_errors.readline()
                f_errors.close()

                    # Ouverture de l'ancien fichier avec les différences entre les 2 versions    
                old_diff_file = open('wormbase/temp/diff_WS' + str(old_release) + '-WS' + str(new_release), 'rb')

                    # Ouverture du nouveau fichier avec les différences, ne contenant que les gènes où une erreur est survenue
                new_diff_file = open('wormbase/temp/diff_WS' + str(old_release) + '-WS' + str(new_release) + '.temp', 'wb')
                          
                line = old_diff_file.readline()
                while (line != "") :
                    sep_line = line.split('\t')
                    if (sep_line[0] in errors) : new_diff_file.write(line)
                    line = old_diff_file.readline()                
             
                new_diff_file.close()
                old_diff_file.close()
              
                    # Remplace l'ancien fichier des différences par le nouveau, et effacement de l'ancien fichier d'erreur                     
                os.remove('wormbase/temp/ACeDB_WS' + str(old_release) + '-WS' + str(new_release) + '.errors')
                os.remove('wormbase/temp/diff_WS' + str(old_release) + '-WS' + str(new_release))
                os.rename('wormbase/temp/diff_WS' + str(old_release) + '-WS' + str(new_release) + '.temp', 'wormbase/temp/diff_WS' + str(old_release) + '-WS' + str(new_release))           
                
                
                # Etat du processus
            self.__process_result = False

                # Récupération des modifications entre les versions
            res = __get_ACeDB_info()

            if (res == True) :
                self.__process_result = True
                return True
             
                # Si erreurs, on crée un nouveau fichier des différences contenant uniquement les gènes où une erreur est survenue
            __create_new_diff_files_from_errors()

                # Relancement de la récupération des modifications automatique (1 seule fois) si option sélectionnée
            if ((self.CFG.getboolean('UPDATE', 'auto_correct') == True) and (recur == False) and (self.__force_to_quit == False)) :
                return __get_changes(old_release, new_release, True)
                
            self.__process_result = True
            return False



        def __get_date_new_release (release) :
            """Récupère la date de parution/disponibilité d'une version de WormBase.
               release : Version de WormBase [int]"""

            def __format_regexp (regexp, release) :

                beg = regexp.find('<release>')
                end = regexp.rfind('/', 0, beg)

                directory = regexp[:end+1]
                filename = regexp[end+1:].replace('<release>', str(release)).replace('\\', '')

                return (directory, filename)


                # Connexion au serveur 
            __FTP2 = FTP_Connection ()
            __FTP2.connection(self.CFG.get('UPDATE', 'letter_host'), self.CFG.get('UPDATE', 'letter_login'), self.CFG.get('UPDATE', 'letter_password'))
                
                # Formate l'expression régulière pour récupérer les noms du dossier et du fichier à télécharger pour la lettre de la release
            directory, filename = __format_regexp(self.CFG.get('UPDATE', 'letter_regexp'), release)

                # Télécharge le fichier contenant la date
            __FTP2.download_file(directory, filename, 'wormbase/temp/letter.WS' + str(release))

                # Déconnexion du serveur
            __FTP2.disconnection()

                # Récupération de la date dans le fichier
            f = open('wormbase/temp/letter.WS' + str(release), 'rb')
            header = f.readline()
            f.close()
            
            exp = ".+ ([a-zA-Z]{3}) +([0-9]+) [0-9]{2}:[0-9]{2}:[0-9]{2} [a-zA-Z]{3} ([0-9]{4})"
            regexp = re.compile(exp)
            
            date = regexp.findall(header)
            
                # Transformation pour renvoi de la date
            mois = {"Jan" : "01", "Feb" : "02", "Mar" : "03", "Apr" : "04", "May" : "05",
                "Jun" : "06", "Jul" : "07", "Aug" : "08", "Sep" : "09", "Oct" : "10",
                "Nov" : "11", "Dec" : "12"}
            
            return [date[0][1], mois[date[0][0]], date[0][2]]	# 'JJ' 'MM' 'AAAA'



        def __create_evol_file (old_release, new_release, date_new_release) :
            """Crée le fichier contenant les évolutions dans le nom des gènes entre les 2 versions de WormBase.
               old_release & new_release : Versions de WormBase.
               date_new_release : Date de la nouvelle release (de <new_release>)"""

                # Conversion des dates en datetime
            date_new = datetime.date(int(date_new_release[2]), int(date_new_release[1]), int(date_new_release[0]))


                # On parcourt toutes les modifications de chaque gène pour récupérer uniquement celui qui a eu lieu entre les 2 versions
            f_acedb = open('wormbase/temp/ACeDB_WS' + str(old_release) + '-WS' + str(new_release), 'rb')
            f_evol = open('wormbase/temp/WS' + str(old_release) + '-WS' + str(new_release), 'wb')

            line = f_acedb.readline()
            evols_gene = []
            while (line != "") :
                evols_gene.append(line.strip().split('\t'))
                
                    # Récupération de toutes les modifications pour un même gène
                line = f_acedb.readline()
                name_old_gene = line.split('\t')[0]
                while (line.split('\t')[0] == evols_gene[0][0]) and (line != "") :
                    evols_gene.append(line.strip().split('\t'))
                    line = f_acedb.readline()

                
                    # Suppression des évolutions impossibles (ex : DEL Imported, NEW Killed)
                real_evol = []
                for evol  in evols_gene :
                    if (evol[1] == 'DEL') and ((evol[3] == 'Killed') or (evol[3] == 'Made_into_transposon') or \
                                               (evol[3] == 'Split_into') or (evol[3] == 'Merged_into')) :
                        real_evol.append(evol)
                    elif (evol[1] == 'NEW') and ((evol[3] == 'Created') or (evol[3] == 'Imported') or \
                                                 (evol[3] == 'Resurrected') or (evol[3] == 'Split_from')) :
                        real_evol.append(evol)       
                        
                        
                    # Enregistrement si une seule évolution restante
                if (len(real_evol) == 1) :
                    
                    if (len(real_evol[0]) == 5) :
                        f_evol.write(real_evol[0][0] + '\t' + real_evol[0][1] + '\t' + real_evol[0][3] + '\t' + real_evol[0][4] + '\r\n')
                    else :
                        f_evol.write(real_evol[0][0] + '\t' + real_evol[0][1] + '\t' + real_evol[0][3] + '\t' + '' + '\r\n')
                
                    evols_gene = []
                    continue


                    # Si plusieurs évolutions restantes, on regarde la date la plus proche du changement de la release (avant)
                regexp = re.compile("^([0-9]+) days.*")
                dated_evols = []
                for evol in real_evol :
                    date = datetime.date(int(evol[2].split('-')[2]), int(evol[2].split('-')[1]), int(evol[2].split('-')[0]))
                    diff = str(date_new - date)
                    if (diff[0] != '-') :
                        dated_evols.append([int(regexp.findall(diff)[0]), evol])
                    
                dated_evols.sort(key=operator.itemgetter(0))        # tri des résultats : recherche résultat le plus proche avant


                    # Si aucune évolution possible trouvée, on inscrit l'erreur dans le fichier
                if (len(dated_evols) == 0) :
                    f_evol.write(evols_gene[0][0] + '\t' + "ERROR : No evolution available" + '\t' + '' + '\t' + '' + '\r\n')
                    evols_gene = []
                    continue

                    # Si la dernière évolution est un Split_into, on récupère tous les Split into de la même date ; ou on prend l'évolution la plus récente
                evols = []
                if (dated_evols[0][1][3] == 'Split_into') :
                    for evol in dated_evols :
                        if (evol[1][3] == 'Split_into') and (evol[0] == dated_evols[0][0]) :
                            evols.append(evol[1])
                else :
                    evols.append(dated_evols[0][1])

                    # Ecriture de/des évolution(s) dans le fichier
                for evol in evols :
                    if (len(evol) == 5) :
                        f_evol.write(evol[0] + '\t' + evol[1] + '\t' + evol[3] + '\t' + evol[4] + '\r\n')
                    else :
                        f_evol.write(evol[0] + '\t' + evol[1] + '\t' + evol[3] + '\t' + '' + '\r\n')
                    

                evols_gene = []


            f_evol.close()
            f_acedb.close()



        def __correct_geneEvols_files (old_release, new_release) :
            """Corrige le fichier geneEvols à cause des problèmes dus aux dates de modifications incorrectes dans la BDD."""

                # Ouverture du fichier geneEvols
            f = open ('wormbase/temp/WS' + str(old_release) + '-WS' + str(new_release), 'rb')

                # Récupération des informations DEL Merged_into
            old_genes_list = []         # gènes ayant subi une fusion
            new_genes_list = []         # gènes dans lesquels s'est faite la fusion
            other_genes = []            # autres changements (NEW, DEL Split to, ...)

            line = f.readline()
            while (line != "") :
                line_split = line.strip().split('\t')

                try :
                        # Recherche uniquement les changements DEL Merged_into
                    if ((line_split[1] == "DEL") & (line_split[2] == "Merged_into")) :
                        old_genes_list.append(line_split[0])
                        new_genes_list.append(line_split[3])
                    else :
                        other_genes.append(line)
                except :            # exception dans le cas où line_split[1] = "ERROR : No evolution available"
                    other_genes.append(line)

                line = f.readline()

            f.close()


                # Création du nouveau fichier geneEvols
            f = open('wormbase/temp/WS' + str(old_release) + '-WS' + str(new_release), 'wb')

                # Rectification des problèmes liés aux dates de modification dans les Merged_into
            for i in range(len(new_genes_list)) :
                if new_genes_list[i] in old_genes_list :
                    index = old_genes_list.index(new_genes_list[i])
                    f.write(old_genes_list[i] + '\tDEL\tMerged_into\t' + new_genes_list[index] + '\r\n')
                else :
                    f.write(old_genes_list[i] + '\tDEL\tMerged_into\t' + new_genes_list[i] + '\r\n')

                # Ajout des autres modifications
            for i in range(len(other_genes)) :
                f.write(other_genes[i])

            f.close()



        def __move_file (src, dest) :
            """Déplace un fichier.
               src & dest : Fichier source et de destination"""

            try :
                fr = open(src, 'rb')    # copie du fichier
                fw = open(dest, 'wb')
                fw.write(fr.read())
                fw.close()
                fr.close()

                os.remove(src)          # suppression du fichier source
            except :
                return False
            else : 
                return True



        def __get_filename (regexp, release) :
            """Récupère le nom du fichier contenu dans un chemin (expression régulière).
               regexp : Expression régulière"""

            beg = regexp.rfind('<release>')
            end = regexp.rfind('/', 0, beg)

            directory = regexp[:end+1]
            filename = regexp[end+1:].replace('<release>', str(release)).replace('\\', '')
            
            return filename




        __FTP = FTP_Connection()        # Instance de la classe FTP_Connection pour le dialogue avec le serveur


            # Vérifie si une MAJ est déjà en cours
        if (self.CFG.getboolean('UPDATE', 'running') == True) :
            return
        else :
            self.__update_running = True
            self.CFG.set('UPDATE', 'running', 'True')


            # Connexion au serveur FTP
        print "\n*** " + str(datetime.date.today()) + " (AAAA-MM-DD) ***\n"
        if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)
        try :
            print self.LANG.get('UPDATER', 'progress_connection')
            __FTP.connection(self.CFG.get('UPDATE', 'ftp_host'), self.CFG.get('UPDATE', 'ftp_login'), self.CFG.get('UPDATE', 'ftp_password'))
        except :
            return self.error(self.LANG.get('UPDATER', 'error_connection') % (self.CFG.get('UPDATE', 'ftp_host'), self.CFG.get('UPDATE', 'ftp_login')), fatal=True)


            # Récupère la liste des releases à installer
        if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)
        try :
            print self.LANG.get('UPDATER', 'progress_new_releases')
            __new_releases = __check_new_releases(__FTP)
        except :
            return self.error(self.LANG.get('UPDATER', 'error_check_new_release') % (self.CFG.get('UPDATE', 'ftp_host'), self.CFG.get('UPDATE', 'ftp_regexp')), fatal=True)

        if (len(__new_releases) == 0) :
            print self.LANG.get('UPDATER', 'no_new_releases')

            # Récupère les informations pour chaque release à installer
        new_releases_installed = []
        for release in __new_releases :
            print '\n' + self.LANG.get('UPDATER', 'progress_installation_inprogress') % (release)

                # Récupération des GeneIDs
            if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)
            try :
                print self.LANG.get('UPDATER', 'progress_geneids') % (release)
                __get_GeneIDs(__FTP, release)
            except :
                self.error(self.LANG.get('UPDATER', 'error_download_geneIDs') % (release, self.CFG.get('UPDATE', 'ftp_host'), self.CFG.get('UPDATE', 'ftp_regexp')))
                continue


                # Création du fichier des gènes différents entre la nouvelle version et la précédente
            if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)  
                    
            print self.LANG.get('UPDATER', 'progress_diff_file') % (release-1, release)
            res = __create_diff_file(release-1, release)
            
            if (res == -1) :
                return self.error(self.LANG.get('UPDATER', 'error_diff_file') % (release-1, 'wormbase/geneIDs/geneIDs.WS' + str(release-1)), fatal=True)
            elif (res > 10000) :
                self.error(self.LANG.get('UPDATER', 'warning_size_diff_file') % (release-1, release))


                # Recherche des modifications apportés par rapport à la version précédente
            if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)    
            
            print self.LANG.get('UPDATER', 'progress_info_changes')      
            res = __get_changes(release-1, release)

            if (res == False) :
                self.error(self.LANG.get('UPDATER', 'error_in_changes') % ('wormbase/temp/diff_WS' + str(release-1) + '-WS' + str(release), 'wormbase/temp/UPDATE_LOG.txt', 'wormbase/temp/UPDATE_LOG_ACeDB.txt'))

                # Vérifie si il a été interrompu
            self.__process_update.wait()
            if (self.__process_result != True) :
                return self.error('\n' + self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)
                
                # Fermeture du processus
            self.__process_update = None
    
            
                # Récupération de la date de la nouvelle version
            if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)       
                     
            try :
                print self.LANG.get('UPDATER', 'progress_date_release') % (release)
                date_new_release = __get_date_new_release (release)
            except :
                self.error(self.LANG.get('UPDATER', 'error_new_date') % (self.CFG.get('UPDATE', 'letter_host'), self.CFG.get('UPDATE', 'letter_login'), '\n', '\n', release, self.CFG.get('UPDATE', 'letter_host'), self.CFG.get('UPDATE', 'letter_regexp')))
                continue


                # On recherche uniquement l'événement qui s'est produit entre les 2 versions (entre les 2 dates de parution, ou la plus probable)
            if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)      
            
            print self.LANG.get('UPDATER', 'progress_evol_file') % (release-1, release)    
            __create_evol_file (release-1, release, date_new_release)
            __correct_geneEvols_files (release-1, release)      # correction des fichiers dus aux erreurs dans la BDD


                # Installation des fichiers créés (copie)
            if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)       
                     
            try :
                print self.LANG.get('UPDATER', 'progress_copy_files')
                res1 = __move_file('wormbase/temp/geneIDs.WS' + str(release), 'wormbase/geneIDs/geneIDs.WS' + str(release))
                res2 = __move_file('wormbase/temp/WS' + str(release-1) + '-WS' + str(release), 'wormbase/geneEvols/' + 'WS' + str(release-1) + '-WS' + str(release))

                if (self.CFG.getboolean('UPDATE', 'save_acedb_file') == True) :
                    __move_file('wormbase/temp/ACeDB_WS' + str(release-1) + '-WS' + str(release), 'wormbase/temp/ACeDB/ACeDB_WS' + str(release-1) + '-WS' + str(release))
                else :
                    os.remove('wormbase/temp/ACeDB_WS' + str(release-1) + '-WS' + str(release))

                    # Effacement des fichiers temporaires
                os.remove('wormbase/temp/' + __get_filename(self.CFG.get('UPDATE', 'ftp_regexp'), release))
                os.remove('wormbase/temp/' + __get_filename(self.CFG.get('UPDATE', 'letter_regexp'), release))
                if (res == True) :
                    os.remove('wormbase/temp/diff_WS' + str(release-1) + '-WS' + str(release))

                    # Vérification que tous les fichiers ont bien été installés
                if (res1 == False) or (res2 == False) : raise

            except :
                self.error(self.LANG.get('UPDATER', 'error_installation'))
                continue


                # Ajout de la release dans la liste des releases installées                          
            if (self.__force_to_quit == True) : return self.error(self.LANG.get('UPDATER', 'error_manual_stop'), fatal=True)   
            
            print self.LANG.get('UPDATER', 'progress_add_new_release') 
            self.CFG.set('WORMBASE', 'releases', self.CFG.get('WORMBASE', 'releases') + ',' + str(release))
            
            print self.LANG.get('UPDATER', 'progress_installation_complete') % (release)


            # Déconnexion du serveur FTP
        __FTP.disconnection()


            # RAZ
        self.__update_running = False
        self.__force_to_quit = False
        self.__process_update = None        
        self.__process_result = False
        self.CFG.set('UPDATE', 'running', 'False')




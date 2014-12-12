#!/usr/bin/perl

####
##  Copyright � 2010 CIML
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

## ARGV[0] : Nom du fichier contenant les différences entre les deux versions de WormBase (gènes ajoutés/supprimés)
## ARGV[1] : Adresse de l'hôte (Base de données)
## ARGV[2] : Port utilisé pour se connecter à la BDD
## ARGV[3] : Login utilisé pour se connecter à la BDD
## ARGV[4] : Mot de passe utilisé pour se connecter à la BDD


use Ace;
$| = 1;			# Flush le buffer STDOUT



	# Supprime les espaces et caractères spéciaux au début et à la fin des chaines de caractères
sub trim($) {
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
}



	# Enregistrement du nom du gène impossible à récupérer sur la BDD (problème QUERY)
sub error {
	my $wbID = $_[0];			# nom du gène posant problème
	my $error = $_[1];			# erreur
	
		# Affichage d'un message d'erreur
	print "error : ".$error."\n\n";
	
		# Enregistrement du nom du gène dans un fichier
	open(F_ERROR, ">>wormbase/temp/ACeDB_".$old_release."-".$new_release.".errors") or die("Cannot open file (ACeDB_".$old_release."-".$new_release.".errors).");
	print F_ERROR $wbID."\r\n";
	close(F_ERROR);
	
	return (["<ERROR>"]);
}


	
	# Connexion à la BDD de WormBase
sub connection_ACeDB {
	print "Opening the database ($host:$port) .... ";

    my $cnx = undef;

    if ($login eq "") { $cnx = Ace->connect(-host => $host, -port => $port) or die("fatal error : ".Ace->error."\n\n"); }
    elsif ($password eq "") { $cnx = Ace->connect(-host => $host, -port => $port, -user => $login) or die("fatal error : ".Ace->error."\n\n"); }
    else { $cnx = Ace->connect(-host => $host, -port => $port, -user => $login, -pass => $password) or die("fatal error : ".Ace->error."\n\n"); }

	print "done\n\n";
	return $cnx;
}



	# Déconnexion de la BDD
sub disconnection_ACeDB {
	print "Closing the database .... ";

	$_[0]->close();

	print "done\n\n";
}



	# Récupération du nom des modifications dans le nom d'un gène
sub get_history_changes_ACeDB {

		# Récupération des arguments
	my $cnx = $_[0];			# handle de connexion
	my $wbID = $_[1];			# nom du gène (WB ID)
	
		# Création de la requête AQL
	my $req = 'select g->Identity[History][Version_change][5]
			         from g in class Gene
			         where g = "'.$wbID.'"';

		# Attente de 3 secondes avant une nouvelle requête (limite du serveur)
#	print "Pending (3 sec) before a query ...\n";	
#	sleep(3);

		# Envoi de la requête AQL
	print "Querying the database (changes) : [".$wbID."] .... ";
	my @res = $cnx->aql($req) or return error($wbID, $cnx->error);

	print "done\n\n";	
	return @res;
}



	# Récupération des dates de modifications dans le nom d'un gène
sub get_history_dates_ACeDB {

		# Récupération des arguments
	my $cnx = $_[0];			# handle de connexion
	my $wbID = $_[1];			# nom du gène (WB ID)
	
		# Création de la requête AQL
	my $req = 'select g->Identity[History][Version_change][2]
			         from g in class Gene
			         where g = "'.$wbID.'"';

		# Attente de 3 secondes avant une nouvelle requête (limite du serveur)
#	print "Pending (3 sec) before a query ...\n";	
#	sleep(3);

		# Envoi de la requête AQL
	print "Querying the database (dates) :   [".$wbID."] .... ";
	my @res = $cnx->aql($req) or return error($wbID, $cnx->error);

	print "done\n\n";	
	return @res;
}



	# Récupération du nom de l'autre gène lié à une modification
sub get_history_details_ACeDB {

		# Récupération des arguments
	my $cnx = $_[0];			# handle de connexion
	my $wbID = $_[1];			# nom du gène (WB ID)
	my $change = $_[2];			# Modification (Merged_into, Acquires_merge, Split_into, Split_from)
	
		# Création de la requête AQL
	my $req = 'select g->Identity[History]['.$change.']
			         from g in class Gene
			         where g = "'.$wbID.'"';

		# Attente de 3 secondes avant une nouvelle requête (limite du serveur)
#	print "Pending (3 sec) before a query ...\n";
#	sleep(3);

		# Envoi de la requête AQL
	print "Querying the database (details) : [".$wbID."] .... ";
	my @res = $cnx->aql($req) or return error($wbID, $cnx->error);

	print "done\n\n";
	return @res;
}





####################  DEBUT DU SCRIPT  ####################

my %months = ("Jan" => "01", "Feb" => "02", "Mar" => "03", "Apr" => "04", "May" => "05",
			"Jun" => "06", "Jul" => "07", "Aug" => "08", "Sep" => "09", "Oct" => "10",
			"Nov" => "11", "Dec" => "12");

	# Récupération des arguments
$diff_file = $ARGV[0];
$host = $ARGV[1];
$port = $ARGV[2];
$login = $ARGV[3];
$password = $ARGV[4];

if ($host eq "") { die("No host specified.\n\n"); }
if ($port eq "") { die("No port specified.\n\n"); }
if ($diff_file eq "") { die("No files of differences specified.\n\n"); }

$diff_file =~ /diff_(WS[0-9]*)-(WS[0-9]*)/;
$old_release = $1;
$new_release = $2;


print "\n => SCRIPT : get_history.pl [$diff_file] .... running\n\n";

	# Ouverture du fichier avec les différences entre les versions (lecture)
open(F_DIFF, "wormbase/temp/".$diff_file) or die("Cannot open file (wormbase/temp/".$diff_file.").");

	# Connexion à la BDD
my $cnx = &connection_ACeDB();

	# Enregistrement de l'historique de chaque gène
while (<F_DIFF>) {

	my @line = split(/\t/, &trim($_));
	my $wbID = $line[0];					# WormBase ID du gène
	my $diff = $line[1];					# Modification (DEL ou NEW)


		# Recherche les modifications dans le nom du gène
	my @changes = &get_history_changes_ACeDB ($cnx, $wbID);
	if ($changes[0][0] eq "<ERROR>") { next; }


		# Recherche l'historique du gène
	@dates = &get_history_dates_ACeDB ($cnx, $wbID);
	if ($dates[0][0] eq "<ERROR>") { next; }
	
	if (scalar(@dates) != scalar(@changes)) {
		&error($wbID, "The number of dates is different than the number of changes. Correct this error manually.");
		next;
	}


		# Recherche le gène associé à chaque modification
	my @details == ();
	for (my $i_change = 0; $i_change < scalar(@changes); $i_change++) {
		
			# Modifications avec gène associé
		if (($changes[$i_change][0] ne "Created") && ($changes[$i_change][0] ne "Imported") && ($changes[$i_change][0] ne "Resurrected") &&
			($changes[$i_change][0] ne "Killed") && ($changes[$i_change][0] ne "Made_into_transposon") && ($changes[$i_change][0] ne "CGC_name") &&
			($changes[$i_change][0] ne "Changed_class")) {

				my @detail = &get_history_details_ACeDB($cnx, $wbID, $changes[$i_change][0]); 
				if ($detail[0][0] eq "<ERROR>")  { last; }

				if (scalar(@detail) == 0) {
					push(@details, ""); 
				}
				else {
					push(@details, $detail[0][0]);
				}
		}
		
			# Modifications sans gène associé
		else {
				push(@details, "");
		}
		
	}
	if (scalar(@details) != scalar(@changes)) { next; }
	
	
		# Enregistrement des informations sur l'historique du gène
	open(F_EVOL, ">>wormbase/temp/ACeDB_".$old_release."-".$new_release) or die("Cannot create file (wormbase/temp/ACeDB_".$old_release."-".$new_release.").");
	for (my $i = 0; $i < scalar(@changes); $i++) {
		
		$dates[$i][0] =~ /^([0-9]{2}) ([a-zA-Z]{3}) ([0-9]{4}) .*/;
		
		print F_EVOL $wbID."\t".$diff."\t".$1."-".$months{$2}."-".$3."\t".$changes[$i][0]."\t".$details[$i]."\r\n";
	}
	close(F_EVOL);

}

	# Déconnexion de la BDD
&disconnection_ACeDB($cnx);


	# Fermeture des fichiers
close(F_DIFF);

print " => SCRIPT : get_history.pl [$diff_file] .... done\n\n";

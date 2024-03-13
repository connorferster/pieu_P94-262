import math
from dataclasses import dataclass
import matplotlib.pyplot as plt


import geotech_module.utils as utils
from geotech_module.solver import NewtonRaphson11
from geotech_module.soil import Soil


TAB_A1 = {
    '1' : {'Classe': 1, 'Abreviation': 'FS',           'Descriptif': 'Foré simple (pieux et barrettes)'},
    '2' : {'Classe': 1, 'Abreviation': 'FB',           'Descriptif': 'Foré boue (pieux et barrettes'},
    '3' : {'Classe': 1, 'Abreviation': 'FTP',          'Descriptif': 'Foré tubé (virole perdue)'},
    '4' : {'Classe': 1, 'Abreviation': 'FTR',          'Descriptif': 'Foré tubé (virole récupérée)'},
    '5' : {'Classe': 1, 'Abreviation': 'FSR, FBR, PU', 'Descriptif': 'Foré simple ou boue avec rainurage ou puits'},
    '6' : {'Classe': 2, 'Abreviation': 'FTC, FTCD',    'Descriptif': 'Foré tarière creuse simple rotation, ou double rotation'},
    '7' : {'Classe': 3, 'Abreviation': 'VM',           'Descriptif': 'Vissé moulé'},
    '8' : {'Classe': 3, 'Abreviation': 'VT',           'Descriptif': 'Vissé tubé'},
    '9' : {'Classe': 4, 'Abreviation': 'BPF, BPR',     'Descriptif': 'Battu béton préfabriqué ou précontraint'},
    '10': {'Classe': 4, 'Abreviation': 'BE',           'Descriptif': 'Battu enrobé (béton - mortier - coulis)'},
    '11': {'Classe': 4, 'Abreviation': 'BM',           'Descriptif': 'Battu moulé'},
    '12': {'Classe': 4, 'Abreviation': 'BAF',          'Descriptif': 'Battu acier fermé'},
    '13': {'Classe': 5, 'Abreviation': 'BAO',          'Descriptif': 'Battu acier ouvert'},
    '14': {'Classe': 6, 'Abreviation': 'HB',           'Descriptif': 'Profilé H battu'},
    '15': {'Classe': 6, 'Abreviation': 'HBi',          'Descriptif': 'Profilé H battu injecté'},
    '16': {'Classe': 7, 'Abreviation': 'PP',           'Descriptif': 'Palplanches battues'},
    '17': {'Classe': 1, 'Abreviation': 'M1',           'Descriptif': 'Micropieu type I'},
    '18': {'Classe': 1, 'Abreviation': 'M3',           'Descriptif': 'Micropieu type II'},
    '19': {'Classe': 8, 'Abreviation': 'PIGU, MIGU',   'Descriptif': 'Pieu ou micropieu injecté mode IGU - Type III'},
    '20': {'Classe': 8, 'Abreviation': 'PIRS, MIRS',   'Descriptif': 'Pieu ou micropieu injecté mode IRS - Type IV'},
}


TAB_F21 = {
    '1' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '2' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '3' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '4' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '5' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '6' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '7' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '8' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '9' : {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '10': {'gamma_rd1_comp': 2.0, 'gamma_rd1_trac': 2.0, 'gamma_rd2': 1.1},
    '11': {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '12': {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '13': {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '14': {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '15': {'gamma_rd1_comp': 2.0, 'gamma_rd1_trac': 2.0, 'gamma_rd2': 1.1},
    '16': {'gamma_rd1_comp': 1.4, 'gamma_rd1_trac': 1.7, 'gamma_rd2': 1.1},
    '17': {'gamma_rd1_comp': 2.0, 'gamma_rd1_trac': 2.0, 'gamma_rd2': 1.1},
    '18': {'gamma_rd1_comp': 2.0, 'gamma_rd1_trac': 2.0, 'gamma_rd2': 1.1},
    '19': {'gamma_rd1_comp': 2.0, 'gamma_rd1_trac': 2.0, 'gamma_rd2': 1.1},
    '20': {'gamma_rd1_comp': 2.0, 'gamma_rd1_trac': 2.0, 'gamma_rd2': 1.1},
}


@dataclass
class SlicePile:
    """
    Elément (ou tranche) de pieu de hauteur delta_h, chargée en tête par une force Q_top, 
    associée à un déplacement imposé y_top.
    Les informations qs et Kt sont fournies en vue d'obtenir les lois de mobilisation du frottement latéral.
    """

    z_top: float
    delta_h: float
    soil: Soil
    data_pieu: dict

    Q_bott = 0.
    dz_bott = 0.
    Q_middle = 0.
    dz_middle = 0.
    Q_top = 0.
    dz_top = 0.

    def set_Q_bott(self, Q_bott: float) -> float:
        """
        Fonction pour modifier la valeur de Q_bott
        """
        self.Q_bott = Q_bott

    def set_dz_bott(self, dz_bott: float) -> float:
        """
        Fonction pour modifier la valeur de dz_bott
        """
        self.dz_bott = dz_bott

    def set_dz_middle(self, dz_middle: float) -> float:
        """
        Fonction pour modifier la valeur de dz_middle
        """
        self.dz_middle = dz_middle

    @property
    def z_middle(self):
        """
        Returns the mid-point level of the slice.
        """
        return self.z_top - self.delta_h / 2

    @property
    def z_bottom(self):
        """
        Returns the bottom level of the slice.
        """
        return self.z_top - self.delta_h

    @property
    def pile_category(self) -> int:
        """
        Catégorie du pieu au sens du tableau A1 de la NF P94-262 - Annexe A
        """
        return self.data_pieu['Categorie']

    @property
    def Eb(self) -> float:
        """
        Module d'Young du matériau constituant la fondation (pour le raccourcissement)
        """
        return self.data_pieu['Eb']

    @property
    def Dp(self) -> float:
        """
        Diamètre équivalent du pieu pour l'effort de pointe (surface)
        """
        return self.data_pieu['Dp']

    @property
    def Ds(self) -> float:
        """
        Diamètre équivalent du pieu pour le frottement (périmètre)
        """
        return self.data_pieu['Ds']

    @property
    def qs_max(self) -> float:
        """
        Valeur du frottement axial unitaire maximal, fonction de la catégorie du pieu - suivant le tableau F.5.2.3 de la NF P94-262.
        """
        return self.soil.frottement_maxi(self.pile_category)

    @property
    def qs_lim(self) -> float:
        """
        Valeur du frottement axial unitaire admissible - suivant l'article F.5.2 de la NF P94-262.
        """
        alpha_pieu_sol = self.soil.alpha_pieu_sol(self.pile_category)
        f_sol = self.soil.fonction_fsol
        qs = alpha_pieu_sol * f_sol
        
        return min(qs, self.qs_max)

    @property
    def module_kt(self) -> float:
        """
        Module kt suivant l'annexe L de la NF P94-262, fonction du type de sol (fin ou granulaire).
        Permet de définir la loi de mobilisation du frottement axial.
        """
        return self.soil.module_kt(self.Ds)

    @property
    def module_kq(self) -> float:
        """
        Module kq suivant l'annexe L de la NF P94-262, fonction du type de sol (fin ou granulaire).
        Permet de définir la loi de mobilisation de l'effort de pointe.
        """
        return self.soil.module_kq(self.Ds)

    @property
    def section_pointe(self) -> float:
        """
        Calcule la section du pieu (ou de la tranche de pieu)
        """
        return math.pi * self.Dp ** 2 / 4

    @property
    def perimetre(self) -> float:
        """
        Calcule le périmètre du pieu (ou de la tranche de pieu)
        """
        return  math.pi * self.Ds

    @property
    def ksi_a(self) -> float:
        """
        Paramètres de calculs : ksi_a = Q_bott * delta_h / (pi * Dp^2 * Eb)
        """
        return 2 * self.Q_bott * self.delta_h / (math.pi * self.Dp**2 * self.Eb)

    @property
    def ksi_b(self) -> float:
        """
        Paramètres de calculs : ksi_b = Ds * delta_h^2 / (2 * Dp^2 * Eb)
        """
        return self.Ds * self.delta_h**2 / (2 * self.Dp**2 * self.Eb)

    def tau_z(self, z: float) -> float:
        """
        Frottement latéral autour du pieu calculé pour un déplacement donné z.
        """
        return utils.skin_friction_law(z, self.qs_lim, self.module_kt)

    def q_z(self, qb: float, z: float) -> float:
        """
        Mobilisation de l'effort de pointe pour un déplacement z donné.
        """
        return utils.end_bearing_law(z, qb, self.module_kq)

    @property
    def Q_middle(self) -> float:
        """
        Effort normal dans le pieu à mi-hauteur de l'élément.
        """
        return self.Q_bott + math.pi * self.Ds * self.delta_h / 2 * self.tau_z(self.dz_middle)

    @property
    def Q_top(self) -> float:
        """
        Effort normal dans le pieu en partie supérieure de l'élément.
        """
        return 2 * self.Q_middle - self.Q_bott

    @property
    def dz_top(self) -> float:
        """
        Déplacement vertical en partie supérieure de l'élément.
        """
        return self.dz_bott + 4 * self.Q_middle * self.delta_h / (math.pi * self.Dp**2 * self.Eb)

    @property
    def qs(self) -> float:
        return self.tau_z(self.dz_middle)

    def fonction_F(self, z: float) -> float:
        """
        Calcul de la fonction F à partir de y.
        F = dz_bott + ksi_a + ksi_b * tau_z(z) - z
        Utilisé pour itérer sur z en vue d'obtenir F = 0
        """
        return self.dz_bott + self.ksi_a + self.ksi_b * self.tau_z(z) - z

    def equilibre(self, dz_bott: float) -> float:
        """
        Calcul l'équilibre d'un tronçon pour un tassement donné
        """
        dz_middle = NewtonRaphson11(self.fonction_F, [0.], [dz_bott]).final_roots
        self.set_dz_middle(dz_middle)

        return self.Q_top, self.dz_top

    def horizontal_soil_pressure_spring(self, dy: float, B: float, situation: str='court terme') -> float:
        """
        Loi de mobilisation de la pression latérale sur le sol.
        La loi renvoyée tient compte de la hauteur de l'élément de pieu.
        """
        situations = ['court terme', 'long terme', 'elu', 'sismique']
        if situation.lower() == situations[0]:
            q1 = self.delta_h * B * self.soil.pf
            k1 = self.delta_h * self.soil.module_kf(B)
        elif situation.lower() == situations[1]:
            q1 = self.delta_h * B * self.soil.pf
            k1 = self.delta_h * self.soil.module_kf(B) / 2
        elif situation.lower() == situations[2]:
            q1 = self.delta_h * B * self.soil.pf
            k1 = self.soil.module_kf(B)
            q2 = self.delta_h * B * self.soil.pl
            k2 = self.delta_h * self.soil.module_kf(B) / 2
        elif situation.lower() == situations[3]:
            q1 = self.delta_h * B * self.soil.pl
            k1 = self.delta_h * self.soil.module_kf(B) * 3
        else:
            return print("Erreur dans la définition de la situation : ['court terme', 'long terme', 'ELU', 'sismique']")

        if q2 == None or k2 == None:
            return utils.tri_linear_law(dy, q1, k1)
        else:
            return utils.tri_linear_law(dy, q1, k1, q2, k2)

    def linear_spring(self, B: float, situation: str='court terme') -> float:
        """
        Returns the stifness of the soil spring assuming a linear spring.
        """
        situations = ['court terme', 'long terme', 'elu', 'sismique']
        if situation.lower() == situations[0]:
            return self.delta_h * self.soil.module_kf(B)
        elif situation.lower() == situations[1]:
            return self.delta_h * self.soil.module_kf(B) / 2
        elif situation.lower() == situations[2]:
            return self.delta_h * self.soil.module_kf(B)
        elif situation.lower() == situations[3]:
            return self.delta_h * self.soil.module_kf(B) * 3
        else:
            return print("Erreur dans la définition de la situation : ['court terme', 'long terme', 'ELU', 'sismique']")


@dataclass
class Pile:
    """
    Classe de pieu (fondation profonde). Le pieu est défini par les paramètres suivants:
        - category:     Catégorie du pieu au sens du tableau A1 de la NF P94-262 - Annexe A
        - level_top:    Niveau supérieur du pieu
        - level_bott:   Niveau inférieur du pieu
        - Eb:           Module de Young du pieu
        - Dp:           Diamètre équivalent du pieu pour l'effort de pointe (surface)
        - Ds:           Diamètre équivalent du pieu pour le frottement (périmètre)
        - lithology:    Couches de sol sur la hauteur du pieu   list[Soil]
        - thickness:    Epaisseur des mailles pour la discretisation du pieu        
    """
    category: int
    level_top: float
    level_bott: float
    Eb: float
    Dp: float
    Ds: float
    lithology: list[Soil]
    thickness: float=0.20

    def __post_init__(self):
        self.slices = self.maillage_pieu()

    @property
    def data_pile(self):
        """
        Dictionnaire pour stocker les données du pieu à passer aux tranches de pieu lors de la discrétisation.
        """
        data_acc = {}
        data_acc.update({'Categorie': self.category})
        data_acc.update({'Eb': self.Eb})
        data_acc.update({'Dp': self.Dp})
        data_acc.update({'Ds': self.Ds})
        return data_acc

    @property
    def pile_classe(self) -> int:
        """
        Renvoie la classe de la fondation (fonction de la catégorie) suivant le tableau A1 de la norme.
        """
        return TAB_A1[str(self.category)]['Classe']

    @property
    def abreviation_pieu(self) -> int:
        """
        Abréviation utilisée dans le tableau A1 de la norme.
        """
        return TAB_A1[str(self.category)]['Abreviation']

    @property
    def description(self) -> int:
        """
        Description de la fondation profonde utilisée dans le tableau A1 de la norme.
        """
        return TAB_A1[str(self.category)]['Descriptif']

    @property
    def height_pile(self):
        """
        Hauteur totale du pieu (N_tete - N_pointe)
        """
        return self.level_top - self.level_bott

    @property
    def section_pointe(self) -> float:
        """
        Returns the section area of the pile.
        """
        return math.pi * self.Dp ** 2 / 4

    @property
    def perimetre(self) -> float:
        """
        Returns the perimetre of the pile.
        """
        return  math.pi * self.Ds

    @property
    def gamma_rd1_comp(self):
        """
        Returns the partial coefficient gamma_rd1_comp.
        """
        return TAB_F21[str(self.category)]['gamma_rd1_comp']

    @property
    def gamma_rd1_trac(self):
        """
        Returns the partial coefficient gamma_rd1_trac.
        """
        return TAB_F21[str(self.category)]['gamma_rd1_trac']

    @property
    def gamma_rd2(self):
        """
        Returns the partial coefficient gamma_rd2.
        """
        return TAB_F21[str(self.category)]['gamma_rd2']

    @property
    def portance_fluage_car(self, coeff_Rb: float=0.5, coeff_Rs: float=0.7) -> float:
        """
        Returns the partial coefficient gamma_rd1_comp.
        """
        return coeff_Rb * self.Rbk + coeff_Rs * self.Rsk_comp

    @property
    def portance_ELS_QP(self, gamma_cr: float=1.1) -> float:
        return self.portance_fluage_car / gamma_cr

    @property
    def portance_ELS_Car(self, gamma_cr: float=0.9) -> float:
        return self.portance_fluage_car / gamma_cr
    
    @property
    def portance_ELU_Str(self, gamma_b: float=1.1, gamma_s: float=1.1) -> float:
        return self.Rbk / gamma_b + self.Rsk_comp / gamma_s

    @property
    def portance_ELU_Acc(self, gamma_b: float=1.0, gamma_s: float=1.0) -> float:
        return self.Rbk / gamma_b + self.Rsk_comp / gamma_s

    @property
    def traction_fluage_car(self, coeff_Rs: float=0.7) -> float:
        return coeff_Rs * self.Rsk_trac

    @property
    def traction_ELS_QP(self, gamma_cr: float=1.5) -> float:
        return self.traction_fluage_car / gamma_cr

    @property
    def traction_ELS_Car(self, gamma_cr: float=1.1) -> float:
        return self.traction_fluage_car / gamma_cr
    
    @property
    def traction_ELU_Str(self, gamma_s: float=1.15) -> float:
        return self.Rsk_trac / gamma_s

    @property
    def traction_ELU_Acc(self, gamma_s: float=1.05) -> float:
        return self.Rsk_trac / gamma_s

    @property
    def resistance_totale(self) -> float:
        """
        Rs + Rb, valeur de résistance totale de la fondation profonde, suivant l'article F.5 de la NF P94-262.
        """
        return self.resistance_pointe + self.resistance_skin_friction

    @property
    def resistance_skin_friction(self) -> float:
        """
        Rs, valeur de résistance de frottement axial de la fondation profonde, suivant l'article F.5 de la NF P94-262.
        """
        Rs_acc = 0
        for slice in self.slices:
            Rs_acc += slice.perimetre * slice.qs_lim * slice.delta_h
        return Rs_acc

    @property
    def Rsk_comp(self) -> float:
        """
        Rs;k, valeur caractéristique de résistance de frottement axial de la fondation profonde, suivant l'article F.5 de la NF P94-262.
        """
        return self.resistance_skin_friction / (self.gamma_rd1_comp * self.gamma_rd2)

    @property
    def Rsk_trac(self) -> float:
        """
        Rs;k, valeur caractéristique de résistance de frottement axial de la fondation profonde, suivant l'article F.5 de la NF P94-262.
        """
        return - self.resistance_skin_friction / (self.gamma_rd1_trac * self.gamma_rd2)

    @property
    def resistance_pointe(self) -> float:
        """
        Rb, valeur de résistance de pointe de la fondation profonde, suivant l'article F.4 de la NF P94-262.
        """
        return self.section_pointe * self.kp_util * self.ple_etoile

    @property
    def Rbk(self) -> float:
        """
        Rb;k, valeur caractéristique de résistance de pointe de la fondation profonde, suivant l'article F.4 de la NF P94-262.
        """
        return self.resistance_pointe / (self.gamma_rd1_comp * self.gamma_rd2)

    @property
    def kp_util(self) -> float:
        """
        kp_util, facteur de portance pressiométrique retenu, fonction de la hauteur d'encastrement effective.
        """
        if self.hauteur_encastrement_effective / self.Ds >= 5:
            return self.kp_max
        else:
            return (1 + (self.kp_max - 1) * self.hauteur_encastrement_effective / (5 * self.Ds))

    @property
    def kp_max(self) -> float:
        """
        kp_max, facteur de portance pressiométrique du pieu, suivant l'article F.4.2 de la NF P94-262.
        """
        return self.get_soil_from_level(self.level_bott).kp_max(self.pile_classe)

    @property
    def ple_etoile(self) -> float:
        """
        Calcul de la pression limite nette équivalente ple* - article F.4.2 (3) de la NF P94-262.
        """
        niveau_haut = self.level_bott + self.b_length
        niveau_bas = self.level_bott - 3 * self.a_longueur
        if niveau_bas < self.courbe_pl[0][-1]:
            return 0.
        return utils.mean_value(self.courbe_pl[0], self.courbe_pl[1],niveau_haut, niveau_bas)

    @property
    def hauteur_encastrement_effective(self) -> float:
        """
        Renvoie la hauteur d'encastrement effective suivant l'équation (F.4.2.6)
        """
        liste_z = self.courbe_pl[0]
        liste_pl = self.courbe_pl[1]
        niveau_haut = self.level_bott + 10 * self.Ds
        niveau_bas = self.level_bott
        return utils.trapezoidal_integration(liste_z, liste_pl, niveau_haut, niveau_bas) / self.ple_etoile

    @property
    def courbe_pl(self) -> list[list[float]]:
        """
        Retourne la courbe des pression limite sur la hauteur du sol sous la forme suivante :
            - une liste pour les abscisses (niveau z);
            - une liste pour les ordonnées (pression limite).
        Afin de permettre le calcul de ple_étoile, il convient que le sol soit défini jusqu'à une profondeur au moins égale à D + 3a
        """
        z_acc = []
        pl_acc = []
        for soil in self.lithology:
            z_acc.append(soil.level_sup)
            z_acc.append(soil.level_inf)
            pl_acc.append(soil.pl)
            pl_acc.append(soil.pl)
        return z_acc, pl_acc

    @property
    def a_longueur(self) -> float:
        """
        Longueur a pour le calcul de la pression limite nette équivalente ple* - article F.4.2 (3) de la NF P94-262. 
        """
        return max(self.Dp / 2, 0.5)

    @property
    def b_length(self) -> float:
        """
        Longueur b pour le calcul de la pression limite nette équivalente ple* - article F.4.2 (3) de la NF P94-262. 
        """
        return min(self.a_longueur, self.height_pile)

    def check_stratigraphy(self) -> bool:
        """
        Vérifie que la stratigraphie du terrain associé au pieu est continue et croissante.
        La vérification porte sur les niveaux 'level_sup' et 'level_inf' renseignés.
        """
        test = 1
        for idx, soil in enumerate(self.lithology):
            if idx == 0:
                level_inf_prec = soil.level_sup
            else:
                level_inf_prec = self.lithology[idx-1].level_inf
            test *= level_inf_prec == soil.level_sup
        return test == 1           

    def get_soil_from_level(self, level: float) -> Soil:
        """
        Renvoie le sol dans la lithographie pour un niveau donné.
        """
        for idx, soil in enumerate(self.lithology):
            if soil.level_inf <= level <= soil.level_sup:
                return soil
        return None

    def get_pf_from_level(self, level: float) -> float:
        """
        Renvoie la pression de fluage pour un niveau donné.
        """
        return self.get_soil_from_level(level).pf

    def get_pl_from_level(self, level: float) -> float:
        """
        Renvoie la pression limite pour un niveau donné.
        """
        return self.get_soil_from_level(level).pl

    def get_Em_from_level(self, level: float) -> float:
        """
        Renvoie le module pressiométrique pour un niveau donné.
        """
        return self.get_soil_from_level(level).Em

    def create_slices(self, thickness: float, level_max, level_min) -> list[SlicePile]:
        """
        Discrétisation du pieu en n "tranches de pieu" d'épaisseur delta_h entre les niveaux level_max et level_min.
        Retourne une liste de "tranches de pieu".
        """
        n_slices = math.ceil((level_max - level_min) / thickness)
        delta_h = (level_max - level_min) / n_slices

        level_top = level_max
        level_bott = level_top - delta_h
        level_middle = (level_top + level_bott) / 2

        slices_acc = []
        i = 0

        while i < n_slices:
            soil = self.get_soil_from_level(level_middle)
            pf = self.get_pf_from_level(level_middle)
            pl = self.get_pl_from_level(level_middle)
            Em = self.get_Em_from_level(level_middle)
            slice = SlicePile(
                z_top = level_top,
                delta_h = delta_h,
                soil = soil,
                data_pieu=self.data_pile
            )
            slices_acc.append(slice)
            level_top -= delta_h
            level_bott -= delta_h
            level_middle -= delta_h
            i += 1

        return slices_acc

    def maillage_pieu(self) -> list[SlicePile]:
        """
        Création des éléments "tranche" sur la hauteur du pieu, en fonction de la stratigraphie du sol.
        """
        slices_acc = []
        for soil in self.lithology:
            level_max = min(self.level_top, soil.level_sup)
            level_min = max(self.level_bott, soil.level_inf)
            if (level_max - level_min) <= 0.:
                continue
            else:
                slice = self.create_slices(self.thickness, level_max, level_min)
                slices_acc = slices_acc + slice
        return slices_acc

    def equilibre_dz_pointe(self, dz_pointe: float) -> list[float | SlicePile]:
        """
        Détermine l'équilibre d'un pieu pour un déplacement vertical donné de la pointe.
        """
        qb = self.kp_util * self.ple_etoile
        q1 = self.slices[-1].section_pointe * self.slices[-1].q_z(qb, dz_pointe)
        dz1 = dz_pointe
        slices = self.slices[::-1]
        for slice in slices:
            slice.set_Q_bott(q1)
            slice.set_dz_bott(dz1)
            equilibre = slice.equilibre(dz1)
            q1 = equilibre[0]
            dz1 = equilibre[1]
        eq_slices = slices[::-1]
        return q1, dz_pointe, dz1, eq_slices
    
    def fonction_effort_en_tete(self, dz_pointe: float) -> float:
        """
        Renvoie l'effort en tête de pieu pour un déplacement donné de la pointe du pieu.
        """
        f_qtop = self.equilibre_dz_pointe(dz_pointe)
        return f_qtop[0]
    
    def equilibre_Q_top(self, q_top: float) -> float:
        """
        """
        solver = NewtonRaphson11(self.fonction_effort_en_tete, [q_top])
        dz_pointe = solver.final_roots
        if dz_pointe == [0.]:
            return None
        return self.equilibre_dz_pointe(dz_pointe)

    def settlement_curve(self, Qmax: float|None=None, nb_pas: float|None=None) -> float:
        """
        Courbe de chargement du pieu, définie par :
            - en abscisse:  la charge en tête
            - en ordonnée:  le tassement en tête du pieu
        """
        if Qmax is None:
            Qmax = self.resistance_totale - 0.0001
        if nb_pas is None:
            nb_pas = 20
        Qi = 1/2 * Qmax / nb_pas
        dz_acc = []
        effort_acc = []
        i = 0
        while i <= nb_pas:
            equilibre = self.equilibre_Q_top(Qi)
            if equilibre == None:
                i += 1
                Qi = i * Qmax / nb_pas
                continue
            else:
                effort = equilibre[3][0].Q_top
                dz_tete = equilibre[3][2].dz_top
                dz_acc.append(dz_tete)
                effort_acc.append(effort)
                i +=1
                Qi = i * Qmax / nb_pas
        return dz_acc, effort_acc

    @property
    def data_for_fe_model(self):
        """
        Returns a dictionary with the pile data required to create de FEModel3D.
        """
        dico = {
            'E': self.Eb,
            'B': 0.25,
            'Iz': 5.84e-6,
            'Iy': 1.,
            'A': 1.,
            'J': 1.,
            'nu': 0.2,
            'rho': 0.,    
        }
        return dico

    def get_fe_model(
            self,
            horizontal_force: float=0.,
            bending_moment: float=0.,
            situation: str='court terme',
        ):
        """
        Returns the PyNite FEModel3D of the pile.
        """
        model = utils.build_pile(self.data_for_fe_model, self.slices, horizontal_force, bending_moment, situation)
        return model

    def pile_description(self):
        """
        Imprime les principales caractéristiques de la fondation profonde dans le terminal
        """
        description = f"\nDescriptif de la fondation profonde :"
        description += f"\n\tType de pieu :\t\t{self.description}"
        description += f"\n\tAbréviation :\t\t{self.abreviation_pieu}"
        description += f"\n\tCatégorie :\t\t{self.category}\t(au sens du tableau A1 de la NF P94-262 - Annexe A)"
        description += f"\n\tClasse :\t\t{self.pile_classe}\t"
        description += f"\n\nGéométrie de la fondation profonde :"
        description += f"\n\tSection :\t\tA ={self.section_pointe: .5f} m²"
        description += f"\n\tPérimètre :\t\tp ={self.perimetre: .4f} m"
        description += f"\n\tHauteur totale :\tH ={self.height_pile: .3f} m"
        description += f"\n\tModule de Young :\tEb ={self.Eb: ,} MPa".replace(',', ' ')
        print(description)

    def capacites_portantes(self):
        """
        Imprime les capacités portantes (compression et traction) de la fondation profonde dans le terminal
        """
        capacites = '\nValeurs caractéristiques de résistance de la fondation profonde :'
        capacites += f"\n\tRb+s\t= {1000 * self.resistance_totale: .1f} kN\tRésistance totale"
        capacites += f"\n\tRb\t= {1000 * self.resistance_pointe: .1f} kN\tRésistance de pointe"
        capacites += f"\n\tRs\t= {1000 * self.resistance_skin_friction: .1f} kN\tRésistance de frottement axial"
        capacites += f"\n\tRb;k\t= {1000 * self.Rbk: .1f} kN\tValeur caractéristique de la résistance de pointe"
        capacites += f"\n\tRs;k_cp\t= {1000 * self.Rsk_comp: .1f} kN\tValeur caractéristique de la résistance de frottement axial (Compression)"
        capacites += f"\n\tRs;k_tr\t= {1000 * self.Rsk_trac: .1f} kN\tValeur caractéristique de la résistance de frottement axial (Traction)"
        capacites += '\n\nCapacité portante de la fondation profonde (Compression) :'
        capacites += f"\n\tELS QP    ≤{1000 * self.portance_ELS_QP: .1f} kN"
        capacites += f"\n\tELS CAR   ≤{1000 * self.portance_ELS_Car: .1f} kN"
        capacites += f"\n\tELU Str   ≤{1000 * self.portance_ELU_Str: .1f} kN"
        capacites += f"\n\tELU Acc   ≤{1000 * self.portance_ELU_Acc: .1f} kN"
        capacites += '\n\nCapacité portante de la fondation profonde (Traction) :'
        capacites += f"\n\tELS QP    ≥ {1000 * self.traction_ELS_QP: .1f} kN"
        capacites += f"\n\tELS CAR   ≥ {1000 * self.traction_ELS_Car: .1f} kN"
        capacites += f"\n\tELU Str   ≥ {1000 * self.traction_ELU_Str: .1f} kN"
        capacites += f"\n\tELU Acc   ≥ {1000 * self.traction_ELU_Acc: .1f} kN"
        print(capacites)


@dataclass
class Torseur:
    """
    Torseur décrivant une charge dans le repère global
    """
    hx: float
    hy: float
    nz: float
    mx: float
    my: float
    situation: str
    comb: str

    def check_situation(self) -> bool:
        """
        Vérification de la validité du paramètre "Situation".
        Doit être parmi ['Durable', 'Transitoire', 'Accidentelle', 'Sismiques'].
        """
        situations = ['Durable', 'Transitoire', 'Accidentelle', 'Sismiques']
        return self.situation.title() in situations

    def check_comb(self) -> bool:
        """
        Vérification de la validité du paramètre "Comb".
        Doit être parmi ['ELS_QP', 'ELS_CAR', 'ELU', 'ELA'].
        """
        if self.situation.title() in ['Durable', 'Transitoire']:
            comb_0 = ['ELS_QP', 'ELS_CAR', 'ELU']
            return self.comb.upper() in comb_0
        elif self.situation.title() in ['Durable', 'Transitoire', 'Accidentelle', 'Sismiques']:
            comb_1 = ['ELA']
            return self.comb.upper() in comb_1
        else:
            return False

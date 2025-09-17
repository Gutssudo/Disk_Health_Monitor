# SMART Disk Health Monitor

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://pypi.org/project/PySide6/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

Un outil de monitoring avancé pour surveiller la santé des disques avec interface graphique moderne, capable d'analyser les données SMART et d'effectuer des benchmarks de performance.

## 🌟 Fonctionnalités

### 📊 Surveillance SMART
- **Support multi-plateformes** : Compatible NVME et SATA/ATA
- **Interface intuitive** : Onglets séparés pour une navigation claire
- **Données en temps réel** : Affichage des attributs SMART critiques
- **Indicateurs visuels** : Code couleur pour l'état de santé (✅/⚠️)
- **Export flexible** : Sauvegarde en JSON et export CSV

### 🚀 Benchmarks de Performance
- **Tests de vitesse** : Mesure des débits de lecture
- **Temps d'accès** : Analyse de la latence du stockage
- **Graphiques interactifs** : Visualisation des performances avec matplotlib
- **Statistiques détaillées** : Moyennes, pics et tendances

### 🎨 Interface Moderne
- **Layout horizontal** : Tableau SMART et données JSON côte à côte
- **Colonnes adaptatives** : Redimensionnement automatique équitable
- **Onglets dédiés** : Séparation claire entre SMART et Benchmark
- **Responsive design** : Interface qui s'adapte à la taille de l'écran

## 🛠️ Installation

### Prérequis
- Python 3.11 ou supérieur
- `smartmontools` installé sur le système :
  ```bash
  # Ubuntu/Debian
  sudo apt install smartmontools

  # RHEL/CentOS
  sudo yum install smartmontools

  # Fedora
  sudo dnf install smartmontools

  # Arch Linux
  sudo pacman -S smartmontools
  ```

### Installation du projet
```bash
# Cloner le projet
cd disk_health
# Créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -e .
pip install -r requirements.txt
```

## 🚀 Utilisation

### Lancement de l'application
```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Lancer l'application
python -m disk_health
```

### Interface utilisateur

#### Onglet SMART
1. **Sélectionner un périphérique** dans la liste déroulante
2. **Cliquer sur "🔍 Vérifier SMART"** pour analyser le disque
3. **Consulter les résultats** :
   - Tableau des attributs SMART avec indicateurs de santé
   - Données JSON brutes pour analyse approfondie
4. **Exporter les données** en CSV ou sauvegarder le rapport JSON

#### Onglet Benchmark
1. **Sélectionner le même périphérique**
2. **Lancer le benchmark** avec le bouton dédié
3. **Suivre la progression** en temps réel
4. **Analyser les résultats** avec graphiques et statistiques

## 🏗️ Architecture

Le projet suit une architecture modulaire respectant les principes SOLID :

```
src/disk_health/
├── ui/                     # Interface utilisateur
│   ├── main_window.py     # Fenêtre principale avec onglets
│   ├── main_tabs.py       # Widget onglets (SMART/Benchmark)
│   ├── device_panel.py    # Sélection des périphériques
│   ├── smart_data_panel.py # Affichage données SMART
│   └── benchmark_panel.py  # Interface benchmark
├── benchmark.py           # Logique de benchmark
├── smart.py              # Analyse SMART
├── utils.py              # Utilitaires système
├── workers.py            # Tâches asynchrones
├── dh_types.py           # Types et dataclasses
├── protocols.py          # Interfaces (typing.Protocol)
└── report_manager.py     # Gestion des rapports
```

### Principes de conception
- **SRP** : Chaque classe a une responsabilité unique
- **Composition over inheritance** : Favorise la composition
- **Type safety** : Typing strict avec mypy
- **Clean code** : Code lisible et maintenable

## 🧪 Tests

Le projet maintient une couverture de tests de 80%+ :

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Tests en mode verbose
pytest -v

# Tests spécifiques
pytest tests/test_smart.py -v
```

### Structure des tests
- **Format Given/When/Then** pour tous les tests
- **Tests paramétrés** pour éviter la duplication
- **Mocks** pour les dépendances externes
- **Fixtures** pour le setup commun

## 🔧 Développement

### Outils de qualité
```bash
# Vérification du code avec ruff
ruff check src/

# Correction automatique
ruff check src/ --fix

# Vérification des types avec mypy
mypy src/

# Tests
pytest
```

### Standards de code
- **Line length** : 88 caractères max
- **Import style** : Imports absolus uniquement
- **Type hints** : Obligatoires partout
- **Docstrings** : Optionnelles mais recommandées pour l'API publique

## 📦 Scripts de gestion

### Gestion des dépendances avec pip-tools
```bash
# Compiler les dépendances
pip-compile pyproject.toml

# Mettre à jour les dépendances
pip-compile --upgrade pyproject.toml

# Synchroniser l'environnement
pip-sync requirements.txt
```

## 🚧 Améliorations Possibles

### Fonctionnalités
- [ ] **Monitoring en continu** : Surveillance automatique avec alertes
- [ ] **Historique des données** : Base de données pour tendances long terme
- [ ] **Notifications** : Alertes système pour événements critiques

### Interface utilisateur
- [ ] **Thèmes** : Mode sombre/clair
- [ ] **Internationalisation** : Support multi-langues
- [ ] **Graphiques avancés** : Plus de types de visualisations
- [ ] **Tableau de bord** : Vue d'ensemble multi-disques
- [ ] **Configuration** : Paramètres utilisateur persistants

### Performance et scalabilité
- [ ] **Cache intelligent** : Mise en cache des résultats SMART
- [ ] **Optimisation mémoire** : Gestion des gros volumes de données
- [ ] **Export avancé** : Plus de formats (PDF, Excel)
- [ ] **API REST** : Interface programmatique
- [ ] **CLI** : Version ligne de commande

### Qualité et maintenance
- [ ] **CI/CD** : Pipeline d'intégration continue
- [ ] **Documentation** : Documentation utilisateur complète
- [ ] **Packaging** : Distribution via PyPI
- [ ] **Sécurité** : Audit de sécurité et permissions
- [ ] **Performance profiling** : Optimisation des goulots d'étranglement

## 🤝 Contribution

Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines de contribution.

## 📋 Prérequis système

### Permissions
L'application nécessite des privilèges d'accès aux périphériques :
- **Linux** : Exécution avec `sudo` ou membre du groupe `disk`
- **Lecture seule** : Accès aux données SMART via `smartctl`

### Dépendances système
- `smartmontools` : Lecture des données SMART
- `lsblk` : Énumération des périphériques (Linux)
- Interface graphique compatible Qt6


## 🔗 Ressources

- [Documentation PySide6](https://doc.qt.io/qtforpython/)
- [Smartmontools](https://www.smartmontools.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
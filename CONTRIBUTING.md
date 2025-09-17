# Guide de Contribution

Merci de votre intérêt pour contribuer au projet SMART Disk Health Monitor ! Ce guide vous aidera à bien débuter.

## 📋 Table des matières

- [Code de conduite](#code-de-conduite)
- [Types de contributions](#types-de-contributions)
- [Configuration de l'environnement](#configuration-de-lenvironnement)
- [Workflow de développement](#workflow-de-développement)
- [Standards de code](#standards-de-code)
- [Tests](#tests)
- [Gestion des dépendances](#gestion-des-dépendances)
- [Documentation](#documentation)
- [Processus de review](#processus-de-review)

## 🤝 Code de conduite

Ce projet adhère à un code de conduite collaboratif. En participant, vous vous engagez à :
- Être respectueux et constructif dans vos interactions
- Accueillir les nouvelles contributions avec bienveillance
- Fournir des commentaires constructifs lors des reviews
- Maintenir un environnement inclusif pour tous

## 🛠️ Types de contributions

Nous accueillons plusieurs types de contributions :

### 🐛 Rapports de bugs
- Utilisez les templates d'issues GitHub
- Incluez des informations système détaillées
- Fournissez des étapes de reproduction claires
- Ajoutez des logs ou captures d'écran si pertinent

### 💡 Demandes de fonctionnalités
- Décrivez le problème que la fonctionnalité résoudrait
- Proposez une solution avec exemples d'usage
- Discutez de l'impact sur l'architecture existante

### 🔧 Corrections de code
- Corrigez des bugs identifiés
- Améliorez les performances
- Refactorisez pour une meilleure maintenabilité

### 📚 Amélioration de la documentation
- Clarifiez les instructions d'installation
- Améliorez les docstrings et commentaires
- Créez des tutoriels ou guides d'usage

## 🏗️ Configuration de l'environnement

### Prérequis
- Python 3.11+
- Git
- `smartmontools` (voir README.md)
- Un éditeur supportant Python (VS Code, PyCharm, etc.)

### Installation pour le développement

1. **Fork et clone**
   ```bash
   git clone https://github.com/Gutssudo/disk_health.git
   cd disk_health
   ```

2. **Environnement virtuel**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Installation avec dépendances de développement**
   ```bash
   pip install -e .
   ```

4. **Installation de pip-tools (recommandé)**
   ```bash
   pip install pip-tools
   ```

5. **Vérification de l'installation**
   ```bash
   # Tests
   pytest

   # Linting
   ruff check src/

   # Type checking
   mypy src/

   # Application
   python -m disk_health
   ```

## 🔄 Workflow de développement

### 1. Préparation
```bash
# Créer une branche pour votre fonctionnalité
git checkout -b feature/ma-nouvelle-fonctionnalite

# Ou pour un bugfix
git checkout -b fix/correction-bug-xyz
```

### 2. Développement
```bash
# Développer avec validation continue
ruff check .        # Style de code
mypy .             # Vérification des types
pytest               # Tests unitaires

# Validation complète avant commit
ruff check . && mypy . && pytest
```

### 3. Commit et push
```bash
# Commits atomiques avec messages descriptifs
git add .
git commit -m "feat: ajouter support pour disques USB

- Détection automatique des périphériques USB
- Support des disques externes
- Tests pour les nouveaux cas d'usage"

git push origin feature/ma-nouvelle-fonctionnalite
```

### 4. Pull Request
- Créez une PR avec un titre clair
- Utilisez le template de PR fourni
- Liez les issues correspondantes
- Demandez une review aux mainteneurs

## 📏 Standards de code

### Style et formatage
Le projet utilise **Ruff** pour l'application des standards :

```bash
# Vérification du style
ruff check src/

# Correction automatique
ruff check src/ --fix
```

#### Règles principales
- **Longueur de ligne** : 88 caractères maximum
- **Imports** : Absolus uniquement, organisés automatiquement
- **Quotes** : Doubles quotes par défaut
- **Trailing commas** : Obligatoires dans les listes multi-lignes

### Architecture et design

#### Principes SOLID
```python
# ✅ Bon : Responsabilité unique
class SmartParser:
    def parse_nvme_data(self, data: dict) -> list[SmartAttribute]:
        ...

# ❌ Mauvais : Multiples responsabilités
class SmartParserAndDisplayer:
    def parse_data(self, data: dict) -> list[SmartAttribute]:
        ...
    def display_in_table(self, attributes: list[SmartAttribute]) -> None:
        ...
```

#### Types et annotations
```python
# ✅ Type hints obligatoires
def calculate_health_score(
    attributes: list[SmartAttribute],
    disk_type: DiskType
) -> HealthScore:
    ...

# ✅ Dataclasses pour les structures
@dataclass
class BenchmarkResult:
    read_speed: float
    access_time: float
    timestamp: datetime
```

#### Gestion d'erreurs
```python
# ✅ Exceptions spécifiques
class SmartDataError(Exception):
    """Erreur lors du parsing des données SMART."""

# ✅ Gestion explicite
try:
    data = parse_smart_output(raw_data)
except SmartDataError as e:
    logger.error(f"Parsing failed: {e}")
    return default_report()
```

## 🧪 Tests

### Organisation des tests
```
tests/
├── test_smart.py           # Tests du module smart
├── test_benchmark.py       # Tests des benchmarks
├── test_utils.py          # Tests des utilitaires
└── conftest.py            # Fixtures communes
```

### Format Given/When/Then
```python
def test_should_parse_nvme_attributes_when_given_valid_json():
    # Given
    json_data = {
        "nvme_smart_health_information_log": {
            "critical_warning": 0,
            "available_spare": 100
        }
    }

    # When
    attributes = parse_nvme_attributes(json_data)

    # Then
    assert len(attributes) == 2
    assert attributes[0].name == "critical_warning"
    assert attributes[0].value == "0"
```

### Tests paramétrés
```python
@pytest.mark.parametrize("input_value,expected", [
    ("100", 100),
    ("0", 0),
    ("invalid", None),
])
def test_safe_int_conversion(input_value: str, expected: int | None):
    # Given/When/Then pattern
    result = safe_int_conversion(input_value)
    assert result == expected
```

### Mocking des dépendances
```python
@patch("disk_health.utils.subprocess.run")
def test_should_return_devices_when_lsblk_succeeds(mock_run):
    # Given
    mock_run.return_value = CompletedProcess(
        args=[], returncode=0, stdout='{"blockdevices": []}'
    )

    # When/Then...
```

### Exécution des tests
```bash
# Tous les tests
pytest

# Tests spécifiques
pytest tests/test_smart.py -v

# Avec couverture
pytest --cov=src --cov-report=html

# En mode watch (développement)
pytest-watch
```

## 📦 Gestion des dépendances

Le projet utilise **pip-tools** pour la gestion déterministe des dépendances.

### Fichiers de dépendances
- `pyproject.toml` : Dépendances déclarées
- `requirements.txt` : Versions lockées (généré)
- `requirements_dev.txt` : Dépendances de dev lockées (généré)

### Workflow avec pip-tools

#### Installation de pip-tools
```bash
pip install pip-tools
```

#### Ajout d'une nouvelle dépendance
1. **Modifier `pyproject.toml`**
   ```toml
   dependencies = [
       "pyside6>=6.7.0",
       "matplotlib>=3.8.0",
       "nouvelle-dependance>=1.0.0",  # Nouvelle ligne
   ]
   ```

2. **Compiler les requirements**
   ```bash
   pip-compile pyproject.toml
   ```

3. **Synchroniser l'environnement**
   ```bash
   pip-sync requirements.txt
   ```

#### Mise à jour des dépendances
```bash
# Mettre à jour toutes les dépendances
pip-compile --upgrade pyproject.toml

# Mettre à jour une dépendance spécifique
pip-compile --upgrade-package pyside6 pyproject.toml

# Synchroniser après mise à jour
pip-sync requirements.txt
```

#### Dépendances de développement
```bash
# Compiler les dépendances de dev
pip-compile --extra=dev pyproject.toml -o requirements-dev.txt

# Synchroniser avec les dépendances de dev
pip-sync requirements.txt requirements-dev.txt
```

### Bonnes pratiques
- **Committez** `requirements.txt` et `requirements-dev.txt`
- **Ne committez pas** le dossier `.venv/`
- **Utilisez des ranges** dans `pyproject.toml` (ex: `>=1.0.0,<2.0.0`)
- **Testez** après chaque mise à jour de dépendance

## 📚 Documentation

### Docstrings
```python
def analyze_smart_data(device: str, timeout: int = 30) -> SmartReport:
    """Analyse les données SMART d'un périphérique.

    Args:
        device: Chemin vers le périphérique (ex: /dev/sda)
        timeout: Timeout en secondes pour la commande

    Returns:
        Rapport SMART complet avec attributs et santé

    Raises:
        SmartctlNotFoundError: Si smartctl n'est pas disponible
        TimeoutError: Si la commande dépasse le timeout
    """
```

### Comments
```python
# Configuration spécifique selon le type de disque
if disk_type == DiskType.NVME:
    # NVME utilise un format différent pour les attributs
    attributes = parse_nvme_format(data)
```

### README et guides
- Maintenez le README.md à jour
- Ajoutez des exemples d'usage
- Documentez les changements breaking

## 🔍 Processus de review

### Préparation de votre PR
- [ ] Tous les tests passent (`pytest`)
- [ ] Code conforme au style (`ruff check src/`)
- [ ] Types validés (`mypy src/`)
- [ ] Documentation mise à jour si nécessaire
- [ ] Changelog mis à jour pour les changements notables

### Checklist du reviewer
- [ ] Code lisible et bien structuré
- [ ] Tests appropriés et suffisants
- [ ] Performance acceptable
- [ ] Sécurité : pas d'exposition de données sensibles
- [ ] Compatibilité : pas de breaking changes non documentés

### Réponse aux commentaires
- Répondez à tous les commentaires de review
- Poussez des commits de correction séparés
- Marquez les conversations comme résolues après correction

## 🚀 Release et deployment

### Versioning
Le projet suit [Semantic Versioning](https://semver.org/) :
- `MAJOR.MINOR.PATCH`
- Incrémentez MAJOR pour breaking changes
- Incrémentez MINOR pour nouvelles fonctionnalités
- Incrémentez PATCH pour bugfixes

### Process de release
1. Mise à jour du CHANGELOG.md
2. Bump de version dans `pyproject.toml`
3. Tag git avec la version
4. Build et publication (automation future)

## ❓ Besoin d'aide ?

- **Documentation** : Consultez le README.md
- **Issues** : Cherchez dans les issues existantes
- **Discussions** : Utilisez les GitHub Discussions
- **Chat** : Rejoignez notre canal de discussion (lien à venir)

## 🎯 Objectifs de contribution

Nous valorisons particulièrement les contributions qui :
- Améliorent l'expérience utilisateur
- Ajoutent du support pour de nouvelles plateformes
- Optimisent les performances
- Renforcent la robustesse et la fiabilité
- Étendent la couverture de tests

Merci de contribuer au projet ! 🚀
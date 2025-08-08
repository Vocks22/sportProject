# 💾 US 2.3 - Export PDF/Excel

> **Status** : 🔴 À FAIRE
> **Points** : 5
> **Sprint** : 6
> **Date prévue** : 16-29 Sept 2025
> **Développeur** : Non assigné
> **Reviewer** : À définir

[[../SCRUM_DASHBOARD|← Dashboard]] | [[../epics/EPIC-2-Advanced|← Epic 2]]

---

## 📝 User Story

### En tant que...
Utilisateur souhaitant analyser mes données

### Je veux...
Pouvoir exporter mes données en formats PDF et Excel

### Afin de...
Conserver des archives, partager avec mon nutritionniste ou analyser dans d'autres outils

---

## 🎯 Acceptance Criteria

- [ ] **Export Planning Hebdomadaire**
  - Format PDF imprimable A4
  - Planning semaine avec recettes
  - Informations nutritionnelles
  - Liste de courses incluse

- [ ] **Export Historique Poids**
  - Excel avec données brutes
  - Graphiques intégrés
  - Statistiques calculées
  - Période personnalisable

- [ ] **Export Rapport Mensuel**
  - PDF professionnel
  - Résumé progression
  - Graphiques et tendances
  - Recommandations

- [ ] **Export Données Complètes (RGPD)**
  - JSON avec toutes données
  - CSV pour tableurs
  - ZIP avec images
  - Conforme RGPD

- [ ] **Options d'export**
  - Sélection période
  - Choix des données
  - Personnalisation format
  - Envoi par email

---

## 🛠️ Solution Technique Proposée

### Génération PDF (Backend)

```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

class PDFExporter:
    def __init__(self, user_id):
        self.user = User.query.get(user_id)
        self.styles = getSampleStyleSheet()
        
    def generate_weekly_plan(self, week_number, year):
        """Génère PDF du planning hebdomadaire"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # En-tête
        story.append(self._create_header(f"Planning Semaine {week_number} - {year}"))
        
        # Planning par jour
        meal_plan = MealPlan.query.filter_by(
            user_id=self.user.id,
            week=week_number,
            year=year
        ).first()
        
        for day in range(1, 8):  # Lundi-Dimanche
            day_meals = self._get_day_meals(meal_plan, day)
            story.append(self._create_day_table(day, day_meals))
        
        # Résumé nutritionnel
        story.append(PageBreak())
        story.append(self._create_nutrition_summary(meal_plan))
        
        # Liste de courses
        story.append(self._create_shopping_list(meal_plan))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_monthly_report(self, month, year):
        """Génère rapport mensuel complet"""
        # Graphiques progression
        weight_chart = self._create_weight_chart(month, year)
        nutrition_chart = self._create_nutrition_chart(month, year)
        
        # Statistiques
        stats = self._calculate_monthly_stats(month, year)
        
        # Génération PDF avec charts
        # ...
```

### Export Excel

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, Reference

class ExcelExporter:
    def export_weight_history(self, user_id, start_date, end_date):
        """Exporte historique poids avec graphiques Excel"""
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Historique Poids"
        
        # Headers avec style
        headers = ['Date', 'Poids (kg)', 'IMC', 'Variation', 'Objectif']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="366092")
            cell.font = Font(color="FFFFFF", bold=True)
        
        # Données
        weights = WeightHistory.query.filter(
            WeightHistory.user_id == user_id,
            WeightHistory.date.between(start_date, end_date)
        ).order_by(WeightHistory.date).all()
        
        for idx, weight in enumerate(weights, 2):
            ws.cell(row=idx, column=1, value=weight.date)
            ws.cell(row=idx, column=2, value=weight.weight)
            ws.cell(row=idx, column=3, value=weight.bmi)
            ws.cell(row=idx, column=4, value=weight.variation)
            ws.cell(row=idx, column=5, value=weight.goal_weight)
        
        # Graphique
        chart = LineChart()
        chart.title = "Evolution du Poids"
        chart.y_axis.title = "Poids (kg)"
        chart.x_axis.title = "Date"
        
        data = Reference(ws, min_col=2, max_col=2, 
                        min_row=1, max_row=len(weights)+1)
        dates = Reference(ws, min_col=1, min_row=2, max_row=len(weights)+1)
        
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(dates)
        ws.add_chart(chart, "G2")
        
        return wb
```

### Frontend Export Manager

```jsx
const ExportManager = () => {
  const [exportType, setExportType] = useState('weekly_plan');
  const [format, setFormat] = useState('pdf');
  const [period, setPeriod] = useState({ start: null, end: null });
  const [loading, setLoading] = useState(false);
  
  const handleExport = async () => {
    setLoading(true);
    
    try {
      const response = await api.post('/api/export', {
        type: exportType,
        format: format,
        period: period,
        options: {
          includeGraphs: true,
          includeStats: true,
          language: 'fr'
        }
      }, {
        responseType: 'blob'
      });
      
      // Téléchargement automatique
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `diettracker_${exportType}_${Date.now()}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Export terminé avec succès!');
    } catch (error) {
      toast.error('Erreur lors de l\'export');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="export-manager">
      <h2>Centre d'Export</h2>
      
      <ExportTypeSelector 
        value={exportType}
        onChange={setExportType}
      />
      
      <FormatSelector
        value={format}
        onChange={setFormat}
        availableFormats={getAvailableFormats(exportType)}
      />
      
      <PeriodSelector
        period={period}
        onChange={setPeriod}
      />
      
      <ExportPreview 
        type={exportType}
        format={format}
        period={period}
      />
      
      <button 
        onClick={handleExport}
        disabled={loading}
        className="btn-primary"
      >
        {loading ? 'Export en cours...' : 'Exporter'}
      </button>
    </div>
  );
};
```

---

## 📊 Types d'Exports Disponibles

### Planning Hebdomadaire PDF
```
📄 Planning_Semaine_32_2025.pdf
├── Page 1: Planning Lundi-Mercredi
├── Page 2: Planning Jeudi-Dimanche  
├── Page 3: Résumé Nutritionnel
└── Page 4: Liste de Courses
```

### Rapport Mensuel PDF
```
📄 Rapport_Aout_2025.pdf
├── Page 1: Résumé Exécutif
├── Page 2: Graphiques Progression
├── Page 3: Statistiques Détaillées
├── Page 4: Recommandations
└── Page 5: Objectifs Mois Suivant
```

### Export Excel Données
```
📈 DietTracker_Data_2025.xlsx
├── Feuille 1: Historique Poids
├── Feuille 2: Mesures Corporelles
├── Feuille 3: Repas Consommés
├── Feuille 4: Statistiques
└── Graphiques intégrés
```

---

## 🧪 Tests

### Tests unitaires
- [ ] Génération PDF valide
- [ ] Export Excel avec formules
- [ ] Encodage caractères spéciaux
- [ ] Taille fichiers optimisée

### Tests d'intégration
- [ ] Export grandes périodes
- [ ] Multi-profils famille
- [ ] Envoi email avec pièce jointe
- [ ] Download sur mobile

### Tests performance
- [ ] Export < 5s pour 1 mois
- [ ] PDF < 5MB
- [ ] Excel < 10MB

---

## 📊 Métriques de Succès

### KPIs
- Exports/utilisateur/mois : > 2
- Formats les plus utilisés : PDF 60%, Excel 30%
- Satisfaction feature : 4.5/5
- Partages nutritionniste : 20%

---

## 🆘 Risques

| Risque | Impact | Mitigation |
|--------|---------|------------|
| Performance serveur | Haut | Queue asynchrone |
| Taille fichiers | Moyen | Compression |
| Compatibilité Excel | Faible | LibreOffice fallback |

---

[[../SCRUM_DASHBOARD|← Dashboard]] | [[US-2.2-Multi-Users|← US 2.2]] | [[US-2.4-Social|US 2.4 →]]
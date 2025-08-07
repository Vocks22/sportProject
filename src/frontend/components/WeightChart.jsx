/**
 * Composant graphique pour l'évolution du poids - US1.7
 * Utilise Recharts pour afficher l'historique des pesées avec ligne d'objectif
 */

import React, { useMemo, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
  Legend
} from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

// Composant tooltip personnalisé
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-medium text-gray-900 mb-1">
          {new Date(label).toLocaleDateString('fr-FR', { 
            day: 'numeric', 
            month: 'long',
            year: 'numeric'
          })}
        </p>
        <div className="space-y-1">
          <p className="text-blue-600 font-medium">
            Poids: {payload[0].value.toFixed(1)} kg
          </p>
          {data.body_fat_percentage && (
            <p className="text-orange-600">
              Masse grasse: {data.body_fat_percentage.toFixed(1)}%
            </p>
          )}
          {data.notes && (
            <p className="text-gray-600 text-sm mt-2 italic">
              {data.notes}
            </p>
          )}
        </div>
      </div>
    );
  }
  return null;
};

// Composant pour afficher les statistiques au-dessus du graphique
const ChartStats = ({ data, targetWeight }) => {
  const stats = useMemo(() => {
    if (!data || data.length === 0) return null;

    const weights = data.map(d => d.weight);
    const minWeight = Math.min(...weights);
    const maxWeight = Math.max(...weights);
    const latestWeight = weights[weights.length - 1];
    const firstWeight = weights[0];
    
    const totalChange = latestWeight - firstWeight;
    const changePercent = ((totalChange / firstWeight) * 100);
    
    return {
      minWeight,
      maxWeight,
      latestWeight,
      firstWeight,
      totalChange,
      changePercent,
      trend: totalChange > 0.5 ? 'up' : totalChange < -0.5 ? 'down' : 'stable'
    };
  }, [data]);

  if (!stats) return null;

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'down': return <TrendingDown className="h-4 w-4 text-green-500" />;
      default: return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'up': return 'text-red-600';
      case 'down': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
      <div className="text-center">
        <div className="text-xs text-gray-500 mb-1">Minimum</div>
        <div className="font-semibold text-blue-600">{stats.minWeight.toFixed(1)} kg</div>
      </div>
      <div className="text-center">
        <div className="text-xs text-gray-500 mb-1">Maximum</div>
        <div className="font-semibold text-red-600">{stats.maxWeight.toFixed(1)} kg</div>
      </div>
      <div className="text-center">
        <div className="text-xs text-gray-500 mb-1">Variation totale</div>
        <div className={`font-semibold flex items-center justify-center gap-1 ${getTrendColor(stats.trend)}`}>
          {getTrendIcon(stats.trend)}
          {stats.totalChange > 0 ? '+' : ''}{stats.totalChange.toFixed(1)} kg
        </div>
      </div>
      <div className="text-center">
        <div className="text-xs text-gray-500 mb-1">Distance objectif</div>
        <div className="font-semibold text-purple-600">
          {targetWeight ? `${Math.abs(stats.latestWeight - targetWeight).toFixed(1)} kg` : '--'}
        </div>
      </div>
    </div>
  );
};

const WeightChart = ({ 
  data = [], 
  targetWeight = null, 
  height = 400, 
  showBodyFat = false,
  showTrendLine = true,
  timeRange = '3M' // 1M, 3M, 6M, 1Y
}) => {
  // Traitement et tri des données
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    // Convertir et trier par date
    const processedData = data
      .map(item => ({
        ...item,
        date: new Date(item.recorded_date).getTime(),
        dateFormatted: new Date(item.recorded_date).toLocaleDateString('fr-FR'),
        weight: parseFloat(item.weight),
        body_fat_percentage: item.body_fat_percentage ? parseFloat(item.body_fat_percentage) : null
      }))
      .sort((a, b) => a.date - b.date);

    // Filtrer par période - basé sur les données disponibles, pas la date actuelle
    let filteredData = processedData;
    
    if (processedData.length > 0) {
      // Utiliser la date la plus récente dans les données comme référence
      const latestDate = Math.max(...processedData.map(item => item.date));
      
      switch (timeRange) {
        case '1M':
          // Afficher les données des 30 derniers jours par rapport à la dernière mesure
          filteredData = processedData.filter(item => 
            (latestDate - item.date) <= (30 * 24 * 60 * 60 * 1000)
          );
          // Si pas assez de données récentes, prendre les 30 dernières mesures
          if (filteredData.length < 5) {
            filteredData = processedData.slice(-30);
          }
          break;
        case '3M':
          // Afficher les données des 90 derniers jours par rapport à la dernière mesure
          filteredData = processedData.filter(item => 
            (latestDate - item.date) <= (90 * 24 * 60 * 60 * 1000)
          );
          // Si pas assez de données récentes, prendre les 90 dernières mesures
          if (filteredData.length < 10) {
            filteredData = processedData.slice(-90);
          }
          break;
        case '6M':
          // Afficher les données des 180 derniers jours par rapport à la dernière mesure
          filteredData = processedData.filter(item => 
            (latestDate - item.date) <= (180 * 24 * 60 * 60 * 1000)
          );
          // Si pas assez de données, prendre toutes les mesures
          if (filteredData.length < 15) {
            filteredData = processedData;
          }
          break;
        case '1Y':
          // Afficher les données de l'année par rapport à la dernière mesure
          filteredData = processedData.filter(item => 
            (latestDate - item.date) <= (365 * 24 * 60 * 60 * 1000)
          );
          break;
        case 'ALL':
        default:
          // Afficher toutes les données
          filteredData = processedData;
          break;
      }
    }

    return filteredData;
  }, [data, timeRange]);

  // Calcul de la ligne de tendance
  const trendLineData = useMemo(() => {
    if (!showTrendLine || chartData.length < 2) return [];
    
    // Régression linéaire simple
    const n = chartData.length;
    const sumX = chartData.reduce((sum, item) => sum + item.date, 0);
    const sumY = chartData.reduce((sum, item) => sum + item.weight, 0);
    const sumXY = chartData.reduce((sum, item) => sum + (item.date * item.weight), 0);
    const sumXX = chartData.reduce((sum, item) => sum + (item.date * item.date), 0);
    
    const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    return chartData.map(item => ({
      date: item.date,
      trend: slope * item.date + intercept
    }));
  }, [chartData, showTrendLine]);

  // Calcul des limites Y avec marge
  const yAxisDomain = useMemo(() => {
    if (chartData.length === 0) return [0, 100];
    
    const weights = chartData.map(d => d.weight);
    const minWeight = Math.min(...weights);
    const maxWeight = Math.max(...weights);
    
    // Ajouter l'objectif dans le calcul
    let allValues = [minWeight, maxWeight];
    if (targetWeight) {
      allValues.push(targetWeight);
    }
    
    const min = Math.min(...allValues);
    const max = Math.max(...allValues);
    const range = max - min;
    const margin = Math.max(range * 0.1, 2); // 10% de marge ou 2kg minimum
    
    return [
      Math.max(0, min - margin),
      max + margin
    ];
  }, [chartData, targetWeight]);

  // Format des dates pour l'axe X
  const formatXAxisLabel = useCallback((tickItem) => {
    const date = new Date(tickItem);
    return date.toLocaleDateString('fr-FR', { 
      day: 'numeric', 
      month: 'short' 
    });
  }, []);

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">📊</div>
          <p className="text-gray-600">Aucune donnée de poids disponible</p>
          <p className="text-gray-400 text-sm">Ajoutez des pesées pour voir votre progression</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Statistiques */}
      <ChartStats data={chartData} targetWeight={targetWeight} />
      
      {/* Graphique */}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey="date"
            type="number"
            scale="time"
            domain={['dataMin', 'dataMax']}
            tickFormatter={formatXAxisLabel}
            stroke="#666"
            tick={{ fontSize: 12 }}
            interval="preserveStartEnd"
          />
          <YAxis 
            domain={yAxisDomain}
            tickFormatter={(value) => `${value.toFixed(1)}kg`}
            stroke="#666"
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Ligne d'objectif */}
          {targetWeight && (
            <ReferenceLine 
              y={targetWeight} 
              stroke="#10b981" 
              strokeDasharray="5 5"
              strokeWidth={2}
              label={{ 
                value: `Objectif: ${targetWeight}kg`, 
                position: "topLeft",
                fill: "#10b981",
                fontSize: 12
              }}
            />
          )}
          
          {/* Ligne de tendance */}
          {showTrendLine && trendLineData.length > 0 && (
            <Line
              data={trendLineData}
              dataKey="trend"
              stroke="#94a3b8"
              strokeWidth={1}
              strokeDasharray="2 2"
              dot={false}
              connectNulls={false}
              type="linear"
            />
          )}
          
          {/* Ligne principale du poids */}
          <Line
            type="monotone"
            dataKey="weight"
            stroke="#3b82f6"
            strokeWidth={3}
            dot={{ 
              fill: '#3b82f6', 
              strokeWidth: 2, 
              r: 4,
              stroke: '#ffffff'
            }}
            activeDot={{ 
              r: 6, 
              stroke: '#3b82f6', 
              strokeWidth: 2, 
              fill: '#ffffff' 
            }}
            connectNulls={false}
          />
          
          {/* Ligne masse grasse si activée */}
          {showBodyFat && (
            <Line
              type="monotone"
              dataKey="body_fat_percentage"
              stroke="#f97316"
              strokeWidth={2}
              dot={{ 
                fill: '#f97316', 
                strokeWidth: 1, 
                r: 3,
                stroke: '#ffffff'
              }}
              connectNulls={false}
            />
          )}
          
          <Legend 
            content={() => (
              <div className="flex flex-wrap justify-center gap-4 mt-4 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span>Poids</span>
                </div>
                {targetWeight && (
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-0.5 bg-green-500" style={{ borderStyle: 'dashed' }}></div>
                    <span>Objectif</span>
                  </div>
                )}
                {showTrendLine && (
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-0.5 bg-gray-400" style={{ borderStyle: 'dashed' }}></div>
                    <span>Tendance</span>
                  </div>
                )}
                {showBodyFat && (
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                    <span>Masse grasse (%)</span>
                  </div>
                )}
              </div>
            )}
          />
        </ComposedChart>
      </ResponsiveContainer>
      
      {/* Informations additionnelles */}
      <div className="mt-4 text-xs text-gray-500 text-center">
        {chartData.length} point{chartData.length > 1 ? 's' : ''} de mesure
        {timeRange !== 'ALL' && ` sur les ${timeRange === '1M' ? 'derniers 30 jours' : 
                                              timeRange === '3M' ? 'derniers 3 mois' : 
                                              timeRange === '6M' ? 'derniers 6 mois' : 
                                              'derniers 12 mois'}`}
      </div>
    </div>
  );
};

// Composant wrapper avec sélection de période
export const WeightChartWithControls = ({ data, targetWeight, ...props }) => {
  // Par défaut, afficher toutes les données si elles sont anciennes
  const defaultTimeRange = React.useMemo(() => {
    if (!data || data.length === 0) return 'ALL';
    
    // Vérifier si les données sont récentes (moins de 90 jours)
    const now = Date.now();
    const latestDate = new Date(Math.max(...data.map(d => new Date(d.recorded_date).getTime())));
    const daysDiff = (now - latestDate) / (1000 * 60 * 60 * 24);
    
    // Si les données les plus récentes ont plus de 30 jours, afficher tout
    return daysDiff > 30 ? 'ALL' : '3M';
  }, [data]);
  
  const [timeRange, setTimeRange] = React.useState(defaultTimeRange);
  const [showBodyFat, setShowBodyFat] = React.useState(false);
  const [showTrendLine, setShowTrendLine] = React.useState(true);
  const [useCustomDates, setUseCustomDates] = React.useState(false);
  const [startDate, setStartDate] = React.useState('');
  const [endDate, setEndDate] = React.useState('');
  
  // Mettre à jour le timeRange si le défaut change
  React.useEffect(() => {
    setTimeRange(defaultTimeRange);
  }, [defaultTimeRange]);

  // Vérifier si on a des données de masse grasse
  const hasBodyFatData = data?.some(item => item.body_fat_percentage);
  
  // Filtrer les données selon les dates personnalisées
  const filteredData = React.useMemo(() => {
    if (!useCustomDates || !startDate || !endDate || !data) return data;
    
    const start = new Date(startDate).getTime();
    const end = new Date(endDate).getTime();
    
    return data.filter(item => {
      const itemDate = new Date(item.recorded_date).getTime();
      return itemDate >= start && itemDate <= end;
    });
  }, [data, useCustomDates, startDate, endDate]);
  
  // Obtenir les dates min et max disponibles
  const dateRange = React.useMemo(() => {
    if (!data || data.length === 0) return { min: '', max: '' };
    
    const dates = data.map(item => new Date(item.recorded_date));
    const minDate = new Date(Math.min(...dates));
    const maxDate = new Date(Math.max(...dates));
    
    return {
      min: minDate.toISOString().split('T')[0],
      max: maxDate.toISOString().split('T')[0]
    };
  }, [data]);

  return (
    <div>
      {/* Contrôles */}
      <div className="space-y-3 mb-4">
        {/* Sélection rapide ou personnalisée */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex gap-1">
            {['1M', '3M', '6M', '1Y', 'ALL'].map((period) => (
              <button
                key={period}
                onClick={() => {
                  setTimeRange(period);
                  setUseCustomDates(false);
                }}
                className={`px-3 py-1 text-sm rounded transition-colors ${
                  !useCustomDates && timeRange === period 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {period === 'ALL' ? 'Tout' : period}
              </button>
            ))}
            <button
              onClick={() => setUseCustomDates(!useCustomDates)}
              className={`px-3 py-1 text-sm rounded transition-colors ${
                useCustomDates
                  ? 'bg-purple-500 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              📅 Personnalisé
            </button>
          </div>
        </div>
        
        {/* Sélecteurs de dates personnalisées */}
        {useCustomDates && (
          <div className="flex flex-wrap items-center gap-2 p-3 bg-purple-50 rounded-lg">
            <label className="text-sm font-medium">Du:</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              min={dateRange.min}
              max={dateRange.max}
              className="px-2 py-1 text-sm border rounded"
            />
            <label className="text-sm font-medium">Au:</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              min={dateRange.min}
              max={dateRange.max}
              className="px-2 py-1 text-sm border rounded"
            />
            {/* Boutons de périodes prédéfinies */}
            <div className="flex gap-1 ml-auto">
              <button
                onClick={() => {
                  const end = new Date();
                  const start = new Date(2025, 6, 1); // Juillet 2025
                  setStartDate(start.toISOString().split('T')[0]);
                  setEndDate(new Date(2025, 6, 31).toISOString().split('T')[0]);
                }}
                className="px-2 py-1 text-xs bg-purple-100 hover:bg-purple-200 rounded"
              >
                Juillet 25
              </button>
              <button
                onClick={() => {
                  setStartDate(new Date(2025, 7, 1).toISOString().split('T')[0]);
                  setEndDate(new Date(2025, 7, 31).toISOString().split('T')[0]);
                }}
                className="px-2 py-1 text-xs bg-purple-100 hover:bg-purple-200 rounded"
              >
                Août 25
              </button>
              <button
                onClick={() => {
                  const now = new Date();
                  const start = new Date(now.getFullYear(), now.getMonth(), 1);
                  setStartDate(start.toISOString().split('T')[0]);
                  setEndDate(now.toISOString().split('T')[0]);
                }}
                className="px-2 py-1 text-xs bg-purple-100 hover:bg-purple-200 rounded"
              >
                Ce mois
              </button>
            </div>
          </div>
        )}
        
        {/* Options d'affichage */}
        <div className="flex flex-wrap items-center justify-between">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={showTrendLine}
                onChange={(e) => setShowTrendLine(e.target.checked)}
                className="rounded"
              />
              Tendance
            </label>
            
            {hasBodyFatData && (
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={showBodyFat}
                  onChange={(e) => setShowBodyFat(e.target.checked)}
                  className="rounded"
                />
                Masse grasse
              </label>
            )}
          </div>
        </div>
      </div>
      
      {/* Graphique */}
      <WeightChart 
        data={useCustomDates ? filteredData : data}
        targetWeight={targetWeight}
        timeRange={useCustomDates ? 'ALL' : timeRange}
        showBodyFat={showBodyFat}
        showTrendLine={showTrendLine}
        {...props}
      />
      
      {/* Info sur la période affichée */}
      {useCustomDates && startDate && endDate && (
        <div className="mt-2 text-sm text-purple-600 text-center">
          Période personnalisée : du {new Date(startDate).toLocaleDateString('fr-FR')} au {new Date(endDate).toLocaleDateString('fr-FR')}
          {filteredData && ` (${filteredData.length} mesures)`}
        </div>
      )}
    </div>
  );
};

export default WeightChart;
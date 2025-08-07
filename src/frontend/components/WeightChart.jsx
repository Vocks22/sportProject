/**
 * Composant graphique pour l'évolution du poids - US1.7
 * Utilise Recharts pour afficher l'historique des pesées avec ligne d'objectif
 */

import React, { useMemo } from 'react';
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

    // Filtrer par période si nécessaire
    const now = Date.now();
    let filteredData = processedData;
    
    switch (timeRange) {
      case '1M':
        filteredData = processedData.filter(item => (now - item.date) <= (30 * 24 * 60 * 60 * 1000));
        break;
      case '3M':
        filteredData = processedData.filter(item => (now - item.date) <= (90 * 24 * 60 * 60 * 1000));
        break;
      case '6M':
        filteredData = processedData.filter(item => (now - item.date) <= (180 * 24 * 60 * 60 * 1000));
        break;
      case '1Y':
        filteredData = processedData.filter(item => (now - item.date) <= (365 * 24 * 60 * 60 * 1000));
        break;
      default:
        break;
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
  const formatXAxisLabel = (tickItem) => {
    const date = new Date(tickItem);
    return date.toLocaleDateString('fr-FR', { 
      day: 'numeric', 
      month: 'short' 
    });
  };

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
  const [timeRange, setTimeRange] = React.useState('3M');
  const [showBodyFat, setShowBodyFat] = React.useState(false);
  const [showTrendLine, setShowTrendLine] = React.useState(true);

  // Vérifier si on a des données de masse grasse
  const hasBodyFatData = data?.some(item => item.body_fat_percentage);

  return (
    <div>
      {/* Contrôles */}
      <div className="flex flex-wrap items-center justify-between mb-4 gap-2">
        <div className="flex gap-1">
          {['1M', '3M', '6M', '1Y', 'ALL'].map((period) => (
            <button
              key={period}
              onClick={() => setTimeRange(period)}
              className={`px-3 py-1 text-sm rounded transition-colors ${
                timeRange === period 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {period === 'ALL' ? 'Tout' : period}
            </button>
          ))}
        </div>
        
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
      
      {/* Graphique */}
      <WeightChart 
        data={data}
        targetWeight={targetWeight}
        timeRange={timeRange}
        showBodyFat={showBodyFat}
        showTrendLine={showTrendLine}
        {...props}
      />
    </div>
  );
};

export default WeightChart;
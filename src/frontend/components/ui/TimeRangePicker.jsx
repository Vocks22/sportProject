import React from 'react';

const TimeRangePicker = ({ value, onChange, className = '' }) => {
  // Parser la valeur existante (format: "7h00-9h00" ou "10h-11h")
  const parseTimeRange = (timeStr) => {
    if (!timeStr) return { startHour: 7, startMin: 0, endHour: 9, endMin: 0 };
    
    const parts = timeStr.split('-');
    if (parts.length !== 2) return { startHour: 7, startMin: 0, endHour: 9, endMin: 0 };
    
    const parseTime = (time) => {
      const match = time.match(/(\d+)h?(\d*)/);
      if (!match) return { hour: 0, min: 0 };
      return {
        hour: parseInt(match[1]) || 0,
        min: parseInt(match[2]) || 0
      };
    };
    
    const start = parseTime(parts[0]);
    const end = parseTime(parts[1]);
    
    return {
      startHour: start.hour,
      startMin: start.min,
      endHour: end.hour,
      endMin: end.min
    };
  };
  
  const { startHour, startMin, endHour, endMin } = parseTimeRange(value);
  
  const handleChange = (field, val) => {
    const current = parseTimeRange(value);
    current[field] = parseInt(val);
    
    // Formater la nouvelle valeur
    const formatTime = (hour, min) => {
      if (min === 0) return `${hour}h`;
      return `${hour}h${min.toString().padStart(2, '0')}`;
    };
    
    const newValue = `${formatTime(current.startHour, current.startMin)}-${formatTime(current.endHour, current.endMin)}`;
    onChange(newValue);
  };
  
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex items-center gap-1">
        <span className="text-sm text-gray-600">De</span>
        <select 
          value={startHour}
          onChange={(e) => handleChange('startHour', e.target.value)}
          className="px-2 py-1 border rounded text-sm"
        >
          {[...Array(24)].map((_, i) => (
            <option key={i} value={i}>{i.toString().padStart(2, '0')}</option>
          ))}
        </select>
        <span className="text-sm">h</span>
        <select 
          value={startMin}
          onChange={(e) => handleChange('startMin', e.target.value)}
          className="px-2 py-1 border rounded text-sm"
        >
          {[...Array(60)].map((_, min) => (
            <option key={min} value={min}>{min.toString().padStart(2, '0')}</option>
          ))}
        </select>
      </div>
      
      <span className="text-sm text-gray-600">à</span>
      
      <div className="flex items-center gap-1">
        <select 
          value={endHour}
          onChange={(e) => handleChange('endHour', e.target.value)}
          className="px-2 py-1 border rounded text-sm"
        >
          {[...Array(24)].map((_, i) => (
            <option key={i} value={i}>{i.toString().padStart(2, '0')}</option>
          ))}
        </select>
        <span className="text-sm">h</span>
        <select 
          value={endMin}
          onChange={(e) => handleChange('endMin', e.target.value)}
          className="px-2 py-1 border rounded text-sm"
        >
          {[...Array(60)].map((_, min) => (
            <option key={min} value={min}>{min.toString().padStart(2, '0')}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default TimeRangePicker;
import { Pipe, PipeTransform } from '@angular/core';

import { StatusLevel } from '../components/status-badge/status-badge.component';

/**
 * Maps alert severity strings to a StatusBadge tone.
 */
@Pipe({ name: 'severityTone' })
export class SeverityTonePipe implements PipeTransform {
  transform(severity: string | undefined | null): StatusLevel {
    switch ((severity ?? '').toLowerCase()) {
      case 'critical': return 'critical';
      case 'warning':  return 'warn';
      case 'info':     return 'info';
      default:         return 'neutral';
    }
  }
}

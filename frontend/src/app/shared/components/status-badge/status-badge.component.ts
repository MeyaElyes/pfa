import { Component, Input } from '@angular/core';

export type StatusLevel = 'ok' | 'warn' | 'critical' | 'info' | 'neutral';

@Component({
  selector: 'app-status-badge',
  templateUrl: './status-badge.component.html',
  styleUrls: ['./status-badge.component.css']
})
export class StatusBadgeComponent {
  @Input() level: StatusLevel = 'neutral';
  @Input() label = '';

  get icon(): string {
    switch (this.level) {
      case 'ok':       return '●';
      case 'warn':     return '●';
      case 'critical': return '●';
      case 'info':     return '●';
      default:         return '○';
    }
  }
}

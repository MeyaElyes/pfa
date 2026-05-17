import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-stat-card',
  templateUrl: './stat-card.component.html',
  styleUrls: ['./stat-card.component.css']
})
export class StatCardComponent {
  @Input() label = '';
  @Input() value: string | number = '';
  @Input() delta?: string;
  @Input() deltaTone: 'neutral' | 'positive' | 'negative' = 'neutral';
}

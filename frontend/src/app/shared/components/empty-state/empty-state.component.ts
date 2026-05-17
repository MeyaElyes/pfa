import { Component, Input } from '@angular/core';

export type EmptyStateTone = 'info' | 'warn' | 'success' | 'error';

@Component({
  selector: 'app-empty-state',
  templateUrl: './empty-state.component.html',
  styleUrls: ['./empty-state.component.css']
})
export class EmptyStateComponent {
  @Input() tone: EmptyStateTone = 'info';
  @Input() title = '';
  @Input() message = '';
}

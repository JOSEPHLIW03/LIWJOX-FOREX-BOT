package com.liwjox.forexbot

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() { override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); setContent { LiwjoxApp() } } }

@Composable fun LiwjoxApp() {
    var running by remember { mutableStateOf(false) }
    var selected by remember { mutableStateOf("Overview") }
    MaterialTheme {
        Scaffold { padding ->
            Column(Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState()).padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Text("LIWJOX", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
                Text("Forex Bot", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
                Text("EUR/USD • Research & demo-first", style = MaterialTheme.typography.bodyMedium)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) { listOf("Overview", "Signals", "Risk").forEach { item -> FilterChip(selected = selected == item, onClick = { selected = item }, label = { Text(item) }) } }
                when(selected) {
                    "Signals" -> { Panel("Market signal", "WAIT", "No live market feed is connected. Signals shown here are not live trading advice."); Panel("Session watch", "London / New York", "Session windows use local market time zones in the research engine.") }
                    "Risk" -> { Panel("Risk mode", "PAPER ONLY", "Real-money trading is not implemented or enabled."); Panel("Limits", "0.5% per simulated trade", "Daily realised-loss lock: 2%. These are prototype defaults, not a promise of safety."); Panel("Emergency stop", "Available locally", "Pause the demo controls below. This screen does not control a remote trading server yet.") }
                    else -> { Panel("Account mode", "DEMO / PAPER ONLY", "No broker account is connected."); Panel("Currency pair", "EUR/USD", "Initial research pair; strategy performance is not validated."); Panel("Today's P/L", "—", "Connect genuine historical or demo data in a later development stage.") }
                }
                Card { Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) { Text("Bot control", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold); Text(if (running) "Paper simulation: locally marked ON" else "Paper simulation: paused"); Button(onClick = { running = !running }, modifier = Modifier.fillMaxWidth()) { Text(if (running) "Pause" else "Start paper mode") }; Text("This toggle is a UI demonstration only. It does not run background trading or place orders.", style = MaterialTheme.typography.bodySmall) } }
                Text("Safety note: trading can lose money. No profits are guaranteed. Live trading is not available in this build.", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable private fun Panel(title: String, value: String, detail: String) { Card { Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) { Text(title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold); Text(value, style = MaterialTheme.typography.headlineSmall); Text(detail, style = MaterialTheme.typography.bodySmall) } } }

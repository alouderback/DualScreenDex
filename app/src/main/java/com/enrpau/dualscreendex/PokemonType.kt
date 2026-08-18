package com.enrpau.dualscreendex

import android.graphics.Color
import androidx.core.graphics.toColorInt

enum class PokemonType(val displayName: String, val colorHex: Int) {
    NORMAL("Normal", "#A8A77A".toColorInt()),
    FIRE("Fire", "#EE8130".toColorInt()),
    WATER("Water", "#6390F0".toColorInt()),
    ELECTRIC("Electric", "#F7D02C".toColorInt()),
    GRASS("Grass", "#7AC74C".toColorInt()),
    ICE("Ice", "#96D9D6".toColorInt()),
    FIGHTING("Fighting", "#C22E28".toColorInt()),
    POISON("Poison", "#A33EA1".toColorInt()),
    GROUND("Ground", "#E2BF65".toColorInt()),
    FLYING("Flying", "#A98FF3".toColorInt()),
    PSYCHIC("Psychic", "#F95587".toColorInt()),
    BUG("Bug", "#A6B91A".toColorInt()),
    ROCK("Rock", "#B6A136".toColorInt()),
    GHOST("Ghost", "#735797".toColorInt()),
    DRAGON("Dragon", "#6F35FC".toColorInt()),
    STEEL("Steel", "#B7B7CE".toColorInt()),
    DARK("Dark", "#705746".toColorInt()),
    FAIRY("Fairy", "#D685AD".toColorInt()),
    AETHER("Aether", "#DEDEC5".toColorInt()),
    UNKNOWN("???", Color.LTGRAY);

    /**
     * Badge label colour for this type. Most type colours are dark enough for white
     * text, but Aether's pale gold is not, so pick by luminance instead of assuming.
     */
    val onColorHex: Int
        get() = contrastTextColorFor(colorHex)

    companion object {
        fun fromString(value: String?): PokemonType {
            return entries.find { it.name.equals(value, ignoreCase = true) }
                ?: entries.find { it.displayName.equals(value, ignoreCase = true) }
                ?: UNKNOWN
        }
    }
}

/**
 * Picks a label colour that stays readable on [background], using WCAG relative
 * luminance. Pale type colours (Aether, Electric, Ice) get dark text; everything
 * else keeps the white the app has always used.
 */
fun contrastTextColorFor(background: Int): Int {
    fun lin(channel: Int): Double {
        val c = channel / 255.0
        return if (c <= 0.03928) c / 12.92 else Math.pow((c + 0.055) / 1.055, 2.4)
    }
    val luminance = 0.2126 * lin(Color.red(background)) +
            0.7152 * lin(Color.green(background)) +
            0.0722 * lin(Color.blue(background))
    return if (luminance > 0.6) "#1A1A1A".toColorInt() else Color.WHITE
}

package com.via.core.storage

import com.via.core.model.FaceProfile
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.flow.first
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class ProfilesPersistenceTest {
    @Test fun threeNamedProfilesRemainAfterRecreatingStorage() = runBlocking {
        val context = RuntimeEnvironment.getApplication()
        val storage = ViaStorage(context)
        storage.saveFaceProfiles(emptyList())
        val profiles = listOf("Ana", "Mihai", "Ștefan").mapIndexed { i, name -> FaceProfile("profile-$i",name,listOf(.1f,.2f),listOf(.3f,.4f),1000L+i) }
        profiles.forEach { storage.addFaceProfile(it) }
        val reopened = ViaStorage(context)
        val saved = reopened.faceProfiles.first()
        assertEquals(3,saved.size)
        assertEquals(listOf("Ana","Mihai","Ștefan"),saved.map { it.displayName })
        assertEquals(profiles.map { it.embedding }, saved.map { it.embedding })
        assertEquals(profiles.map { it.palmEmbedding }, saved.map { it.palmEmbedding })
        reopened.addFaceProfile(profiles[0].copy(displayName = "Ana Maria"))
        val updated = ViaStorage(context).faceProfiles.first()
        assertEquals(3,updated.size)
        assertEquals("Ana Maria",updated.first { it.id=="profile-0" }.displayName)
    }
}

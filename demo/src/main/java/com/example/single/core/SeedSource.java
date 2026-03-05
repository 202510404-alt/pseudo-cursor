package com.example.single.core;

/**
 * 랜덤 시드를 제공하는 추상화입니다.
 * - 싱글: 로컬에서 시드를 생성(LocalSeedSource)
 * - 멀티: 서버에서 시드를 받아오는 RemoteSeedSource로 확장 예정
 */
public interface SeedSource {

    long nextSeed();

}


package com.example.single.core;

/**
 * 한 장의 카드를 표현하는 데이터 구조입니다.
 * card.csv의 한 줄과 1:1로 매핑됩니다.
 *
 * 컬럼:
 * No,Name,Grade,CostType,CostVal,Atk,Hp,Def,Spd,TurnGauge,EnergyTick,Trait,Desc
 */
public class CardDef {

    public final int no;          // 카드 번호
    public final String name;     // 이름
    public final int grade;       // 희귀도
    public final int costType;    // 코스트 종류 (골드/피 등)
    public final int costVal;     // 코스트 수치
    public final int atk;         // 공격력
    public final int hp;          // 체력
    public final int def;         // 방어력
    public final int spd;         // 속도
    public final int turnGauge;   // 행동에 필요한 게이지
    public final int energyTick;  // 기계 유닛일 경우 틱당 에너지 소모량
    public final int trait;       // 특성 (종족/부착물 등)
    public final String desc;     // 설명

    public CardDef(
            int no,
            String name,
            int grade,
            int costType,
            int costVal,
            int atk,
            int hp,
            int def,
            int spd,
            int turnGauge,
            int energyTick,
            int trait,
            String desc
    ) {
        this.no = no;
        this.name = name;
        this.grade = grade;
        this.costType = costType;
        this.costVal = costVal;
        this.atk = atk;
        this.hp = hp;
        this.def = def;
        this.spd = spd;
        this.turnGauge = turnGauge;
        this.energyTick = energyTick;
        this.trait = trait;
        this.desc = desc;
    }
}


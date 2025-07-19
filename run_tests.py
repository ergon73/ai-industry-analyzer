#!/usr/bin/env python3
# run_tests.py - Скрипт для запуска всех тестов

import subprocess
import sys
import os

def run_tests():
    """Запускает все тесты проекта"""
    
    print("🧪 ЗАПУСК ТЕСТОВ AI NEWS ANALYZER")
    print("=" * 50)
    
    # Проверяем наличие pytest
    try:
        import pytest
        print("✅ pytest установлен")
    except ImportError:
        print("❌ pytest не установлен. Установите: pip install pytest")
        return False
    
    # Запускаем тесты
    test_results = []
    
    # 1. Базовые тесты V1
    print("\n📋 Запуск базовых тестов V1...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_v1_basic.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Базовые тесты V1 прошли успешно")
            test_results.append(("V1 Basic", True))
        else:
            print("❌ Базовые тесты V1 провалились")
            print(result.stdout)
            print(result.stderr)
            test_results.append(("V1 Basic", False))
    except Exception as e:
        print(f"❌ Ошибка запуска тестов V1: {e}")
        test_results.append(("V1 Basic", False))
    
    # 2. Продвинутые тесты V2
    print("\n📋 Запуск продвинутых тестов V2...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_v2_advanced.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Продвинутые тесты V2 прошли успешно")
            test_results.append(("V2 Advanced", True))
        else:
            print("❌ Продвинутые тесты V2 провалились")
            print(result.stdout)
            print(result.stderr)
            test_results.append(("V2 Advanced", False))
    except Exception as e:
        print(f"❌ Ошибка запуска тестов V2: {e}")
        test_results.append(("V2 Advanced", False))
    
    # 3. Интеграционные тесты
    print("\n📋 Запуск интеграционных тестов...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_integration.py", 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Интеграционные тесты прошли успешно")
            test_results.append(("Integration", True))
        else:
            print("❌ Интеграционные тесты провалились")
            print(result.stdout)
            print(result.stderr)
            test_results.append(("Integration", False))
    except Exception as e:
        print(f"❌ Ошибка запуска интеграционных тестов: {e}")
        test_results.append(("Integration", False))
    
    # 4. Все тесты вместе
    print("\n📋 Запуск всех тестов...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Все тесты прошли успешно")
            test_results.append(("All Tests", True))
        else:
            print("❌ Некоторые тесты провалились")
            print(result.stdout)
            print(result.stderr)
            test_results.append(("All Tests", False))
    except Exception as e:
        print(f"❌ Ошибка запуска всех тестов: {e}")
        test_results.append(("All Tests", False))
    
    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ТЕСТОВ")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ ПРОШЕЛ" if success else "❌ ПРОВАЛЕН"
        print(f"{test_name:<20} {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Результат: {passed}/{total} тестов прошли успешно")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return True
    else:
        print("⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 